"""Report-related Pydantic schemas."""

from datetime import datetime
from typing import Optional, Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.report import ReportStatus


class ReportCreate(BaseModel):
    """Schema for report generation request."""

    template_id: UUID = Field(..., description="Template to use for report")
    params: Optional[dict[str, Any]] = Field(
        default=None, description="Report generation parameters"
    )

    # Data source configuration
    data_source: Optional[str] = Field(
        default=None,
        description="Data source type: 'sql', 'api', 'csv', or None for sample data",
    )
    data_config: Optional[dict[str, Any]] = Field(
        default=None,
        description="Configuration for data source (query, url, file_path, etc.)",
    )


class ReportResponse(BaseModel):
    """Schema for report response."""

    id: UUID
    user_id: UUID
    template_id: Optional[UUID] = None
    status: ReportStatus
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    params: Optional[dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ReportStatusResponse(BaseModel):
    """Schema for report status check."""

    id: UUID
    status: ReportStatus
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ReportListResponse(BaseModel):
    """Schema for paginated report list."""

    items: list[ReportResponse]
    total: int
    page: int
    page_size: int
    pages: int
