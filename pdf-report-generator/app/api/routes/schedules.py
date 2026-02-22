"""Schedules API endpoints."""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.template import Template
from app.models.schedule import Schedule
from app.schemas.schedule import (
    ScheduleCreate,
    ScheduleResponse,
    ScheduleUpdate,
    ScheduleListResponse,
)
from app.services.scheduler import SchedulerService


router = APIRouter(prefix="/schedules", tags=["Schedules"])


async def execute_scheduled_report(schedule_id: UUID):
    """Execute a scheduled report generation."""
    from app.core.database import async_session_factory
    from app.models.report import Report, ReportStatus
    from app.services.report_generator import ReportGeneratorService

    async with async_session_factory() as session:
        try:
            # Get schedule
            schedule = await session.get(Schedule, schedule_id)
            if not schedule or not schedule.is_active:
                return

            # Create report
            report = Report(
                user_id=schedule.user_id,
                template_id=schedule.template_id,
                status=ReportStatus.PENDING,
                params=schedule.params,
            )
            session.add(report)
            await session.commit()
            await session.refresh(report)

            # Generate report
            await ReportGeneratorService.generate_report(session, report.id)

            # Update schedule
            schedule.last_run = datetime.now(timezone.utc)
            schedule.next_run = SchedulerService.get_next_run_time(
                schedule.cron_expression
            )
            await session.commit()

            logger.info(f"Scheduled report executed: {schedule_id}")

        except Exception as e:
            logger.error(f"Scheduled report failed: {schedule_id}, error: {e}")
            await session.rollback()


@router.post(
    "",
    response_model=ScheduleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new schedule",
)
async def create_schedule(
    request: ScheduleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new scheduled report.

    - **name**: Human-readable name for the schedule
    - **template_id**: UUID of the template to use
    - **cron_expression**: Cron expression (e.g., "0 8 * * *" for daily at 8 AM)
    - **params**: Optional parameters for report generation
    - **is_active**: Whether the schedule is active

    **Cron Expression Format**: minute hour day month day_of_week
    - "0 8 * * *" - Every day at 8:00 AM
    - "0 9 * * 1" - Every Monday at 9:00 AM
    - "0 0 1 * *" - First day of every month at midnight
    """
    # Verify template exists
    template = await db.get(Template, request.template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )

    # Calculate next run time
    next_run = SchedulerService.get_next_run_time(request.cron_expression)

    # Create schedule
    schedule = Schedule(
        user_id=current_user.id,
        template_id=request.template_id,
        name=request.name,
        cron_expression=request.cron_expression,
        params=request.params,
        is_active=request.is_active,
        next_run=next_run,
    )

    db.add(schedule)
    await db.commit()
    await db.refresh(schedule)

    # Add job to scheduler if active
    if schedule.is_active:
        SchedulerService.add_job(
            job_id=str(schedule.id),
            func=execute_scheduled_report,
            cron_expression=schedule.cron_expression,
            args=(schedule.id,),
        )

    logger.info(f"Schedule created: {schedule.id} by user {current_user.email}")

    return ScheduleResponse.model_validate(schedule)


@router.get(
    "",
    response_model=ScheduleListResponse,
    summary="List schedules",
)
async def list_schedules(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all schedules for the current user.
    """
    result = await db.execute(
        select(Schedule)
        .where(Schedule.user_id == current_user.id)
        .order_by(Schedule.created_at.desc())
    )
    schedules = result.scalars().all()

    return ScheduleListResponse(
        items=[ScheduleResponse.model_validate(s) for s in schedules],
        total=len(schedules),
    )


@router.get(
    "/{schedule_id}",
    response_model=ScheduleResponse,
    summary="Get schedule details",
)
async def get_schedule(
    schedule_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get details of a specific schedule.
    """
    schedule = await db.get(Schedule, schedule_id)

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found",
        )

    if schedule.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    return ScheduleResponse.model_validate(schedule)


@router.put(
    "/{schedule_id}",
    response_model=ScheduleResponse,
    summary="Update a schedule",
)
async def update_schedule(
    schedule_id: UUID,
    request: ScheduleUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update an existing schedule.

    Only provided fields will be updated.
    """
    schedule = await db.get(Schedule, schedule_id)

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found",
        )

    if schedule.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    # Update fields
    update_data = request.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(schedule, field, value)

    # Recalculate next run if cron changed
    if "cron_expression" in update_data:
        schedule.next_run = SchedulerService.get_next_run_time(schedule.cron_expression)

    await db.commit()
    await db.refresh(schedule)

    # Update scheduler job
    SchedulerService.remove_job(str(schedule.id))
    if schedule.is_active:
        SchedulerService.add_job(
            job_id=str(schedule.id),
            func=execute_scheduled_report,
            cron_expression=schedule.cron_expression,
            args=(schedule.id,),
        )

    logger.info(f"Schedule updated: {schedule_id}")

    return ScheduleResponse.model_validate(schedule)


@router.delete(
    "/{schedule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a schedule",
)
async def delete_schedule(
    schedule_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a schedule.
    """
    schedule = await db.get(Schedule, schedule_id)

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found",
        )

    if schedule.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    # Remove from scheduler
    SchedulerService.remove_job(str(schedule.id))

    # Delete record
    await db.delete(schedule)
    await db.commit()

    logger.info(f"Schedule deleted: {schedule_id}")
