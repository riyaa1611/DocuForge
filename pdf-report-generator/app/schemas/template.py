"""Template-related Pydantic schemas."""

from datetime import datetime
from typing import Optional, Any
from uuid import UUID

from pydantic import BaseModel, Field


class TemplateResponse(BaseModel):
    """Schema for template list response."""

    id: UUID
    name: str
    description: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class TemplateDetail(BaseModel):
    """Schema for template detail response with schema info."""

    id: UUID
    name: str
    description: Optional[str] = None
    html_path: str
    schema: Optional[dict[str, Any]] = Field(
        default=None, description="Expected data structure for this template"
    )
    created_at: datetime

    model_config = {"from_attributes": True}
