"""Templates API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.template import Template
from app.schemas.template import TemplateResponse, TemplateDetail


router = APIRouter(prefix="/templates", tags=["Templates"])


@router.get(
    "",
    response_model=list[TemplateResponse],
    summary="List available templates",
)
async def list_templates(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a list of all available report templates.
    """
    result = await db.execute(select(Template).order_by(Template.name))
    templates = result.scalars().all()
    
    return [TemplateResponse.model_validate(t) for t in templates]


@router.get(
    "/{template_id}",
    response_model=TemplateDetail,
    summary="Get template details",
)
async def get_template(
    template_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed information about a specific template,
    including its expected data schema.
    """
    template = await db.get(Template, template_id)
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )
    
    return TemplateDetail.model_validate(template)
