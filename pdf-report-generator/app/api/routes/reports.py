"""Reports API endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
import io

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.report import Report, ReportStatus
from app.models.template import Template
from app.schemas.report import (
    ReportCreate,
    ReportResponse,
    ReportStatusResponse,
    ReportListResponse,
)
from app.services.report_generator import ReportGeneratorService
from app.services.storage import StorageService


router = APIRouter(prefix="/reports", tags=["Reports"])


async def process_report_background(report_id: UUID):
    """Background task for report generation."""
    from app.core.database import async_session_factory
    
    async with async_session_factory() as session:
        try:
            await ReportGeneratorService.generate_report(session, report_id)
            await session.commit()
        except Exception as e:
            logger.error(f"Background report generation failed: {e}")
            await session.rollback()


@router.post(
    "/generate",
    response_model=dict,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Generate a new report",
)
async def generate_report(
    request: ReportCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Start generating a new PDF report.
    
    The report is generated asynchronously in the background.
    Use the returned `job_id` to check status and download the result.
    
    - **template_id**: UUID of the template to use
    - **params**: Optional parameters for report generation
    - **data_source**: Optional data source type ('sql', 'api', 'csv')
    - **data_config**: Optional configuration for the data source
    """
    # Verify template exists
    template = await db.get(Template, request.template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )
    
    # Create report record
    report = Report(
        user_id=current_user.id,
        template_id=request.template_id,
        status=ReportStatus.PENDING,
        params={
            "data_source": request.data_source,
            "data_config": request.data_config,
            "context": request.params,
        } if request.data_source or request.params else None,
    )
    
    db.add(report)
    await db.commit()
    await db.refresh(report)
    
    logger.info(f"Report created: {report.id} by user {current_user.email}")
    
    # Start background generation
    background_tasks.add_task(process_report_background, report.id)
    
    return {
        "job_id": str(report.id),
        "status": report.status.value,
        "message": "Report generation started",
    }


@router.get(
    "",
    response_model=ReportListResponse,
    summary="List reports",
)
async def list_reports(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status_filter: Optional[ReportStatus] = Query(None, description="Filter by status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all reports for the current user with pagination.
    
    - **page**: Page number (starts at 1)
    - **page_size**: Number of items per page (max 100)
    - **status_filter**: Optional status filter
    """
    # Build query
    query = select(Report).where(Report.user_id == current_user.id)
    count_query = select(func.count(Report.id)).where(Report.user_id == current_user.id)
    
    if status_filter:
        query = query.where(Report.status == status_filter)
        count_query = count_query.where(Report.status == status_filter)
    
    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Get paginated results
    offset = (page - 1) * page_size
    query = query.order_by(desc(Report.created_at)).offset(offset).limit(page_size)
    
    result = await db.execute(query)
    reports = result.scalars().all()
    
    return ReportListResponse(
        items=[ReportResponse.model_validate(r) for r in reports],
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get(
    "/{report_id}",
    response_model=ReportResponse,
    summary="Get report details",
)
async def get_report(
    report_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get details of a specific report.
    """
    report = await db.get(Report, report_id)
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )
    
    if report.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    return report


@router.get(
    "/{report_id}/status",
    response_model=ReportStatusResponse,
    summary="Check report status",
)
async def get_report_status(
    report_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Check the generation status of a report.
    """
    report = await db.get(Report, report_id)
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )
    
    if report.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    return ReportStatusResponse(
        id=report.id,
        status=report.status,
        error_message=report.error_message,
        started_at=report.started_at,
        completed_at=report.completed_at,
    )


@router.get(
    "/{report_id}/download",
    summary="Download report PDF",
)
async def download_report(
    report_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Download the generated PDF report.
    
    Only available for reports with status 'completed'.
    """
    report = await db.get(Report, report_id)
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )
    
    if report.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    if report.status != ReportStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Report is not ready. Current status: {report.status.value}",
        )
    
    if not report.file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report file not found",
        )
    
    # Get PDF content
    pdf_bytes = await StorageService.get_pdf(report.file_path)
    if not pdf_bytes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report file not found on disk",
        )
    
    # Generate filename
    filename = f"report_{report_id.hex[:8]}.pdf"
    
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Length": str(len(pdf_bytes)),
        },
    )


@router.delete(
    "/{report_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a report",
)
async def delete_report(
    report_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a report and its associated PDF file.
    """
    report = await db.get(Report, report_id)
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )
    
    if report.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    # Delete file if exists
    if report.file_path:
        StorageService.delete_pdf(report.file_path)
    
    # Delete record
    await db.delete(report)
    await db.commit()
    
    logger.info(f"Report deleted: {report_id}")
