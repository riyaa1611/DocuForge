"""Schedule-related Pydantic schemas."""

from datetime import datetime
from typing import Optional, Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator
from croniter import croniter


class ScheduleCreate(BaseModel):
    """Schema for schedule creation."""

    name: str = Field(..., min_length=1, max_length=100, description="Schedule name")
    template_id: UUID = Field(..., description="Template to use for scheduled reports")
    cron_expression: str = Field(
        ..., description="Cron expression (e.g., '0 8 * * *' for daily at 8 AM)"
    )
    params: Optional[dict[str, Any]] = Field(
        default=None, description="Report generation parameters"
    )
    is_active: bool = Field(default=True, description="Whether schedule is active")

    @field_validator("cron_expression")
    @classmethod
    def validate_cron(cls, v: str) -> str:
        """Validate cron expression format."""
        try:
            croniter(v)
        except (KeyError, ValueError) as e:
            raise ValueError(f"Invalid cron expression: {e}")
        return v


class ScheduleUpdate(BaseModel):
    """Schema for schedule update."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    cron_expression: Optional[str] = None
    params: Optional[dict[str, Any]] = None
    is_active: Optional[bool] = None

    @field_validator("cron_expression")
    @classmethod
    def validate_cron(cls, v: Optional[str]) -> Optional[str]:
        """Validate cron expression format if provided."""
        if v is not None:
            try:
                croniter(v)
            except (KeyError, ValueError) as e:
                raise ValueError(f"Invalid cron expression: {e}")
        return v


class ScheduleResponse(BaseModel):
    """Schema for schedule response."""

    id: UUID
    user_id: UUID
    template_id: UUID
    name: str
    cron_expression: str
    params: Optional[dict[str, Any]] = None
    is_active: bool
    next_run: Optional[datetime] = None
    last_run: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ScheduleListResponse(BaseModel):
    """Schema for paginated schedule list."""

    items: list[ScheduleResponse]
    total: int
