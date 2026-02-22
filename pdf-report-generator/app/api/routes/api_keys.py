"""API Key management endpoints."""

import secrets
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import datetime

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.core.security import hash_password
from loguru import logger


router = APIRouter(prefix="/api-keys", tags=["API Keys"])


class APIKeyResponse(BaseModel):
    """API Key response model."""
    id: UUID
    key: str
    name: str
    created_at: datetime
    last_used: Optional[datetime] = None


class APIKeyCreate(BaseModel):
    """API Key creation request."""
    name: str


@router.get("/", response_model=List[dict])
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all API keys for the current user.
    Note: Only returns masked keys for security.
    """
    # In a real implementation, you'd have an APIKey model
    # For now, we'll return the user's API key if it exists
    if current_user.api_key:
        return [{
            "id": str(current_user.id),
            "key": f"{current_user.api_key[:8]}...{current_user.api_key[-4:]}",
            "name": "Primary API Key",
            "created_at": current_user.created_at.isoformat(),
            "last_used": None
        }]
    return []


@router.post("/generate", response_model=dict)
async def generate_api_key(
    request: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a new API key for the current user.
    
    ⚠️ IMPORTANT: Save this key securely - it won't be shown again!
    """
    # Generate a secure random API key
    api_key = f"pdfgen_{secrets.token_urlsafe(32)}"
    
    # Update user with new API key
    current_user.api_key = api_key
    await db.commit()
    await db.refresh(current_user)
    
    logger.info(f"Generated API key for user {current_user.email}")
    
    return {
        "message": "API key generated successfully",
        "api_key": api_key,
        "warning": "Save this key securely - it will not be shown again!"
    }


@router.delete("/{key_id}")
async def revoke_api_key(
    key_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Revoke an API key.
    """
    if str(current_user.id) != str(key_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    current_user.api_key = None
    await db.commit()
    
    logger.info(f"Revoked API key for user {current_user.email}")
    
    return {"message": "API key revoked successfully"}


@router.post("/regenerate", response_model=dict)
async def regenerate_api_key(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Regenerate the API key (revokes old one).
    """
    # Generate new API key
    api_key = f"pdfgen_{secrets.token_urlsafe(32)}"
    
    current_user.api_key = api_key
    await db.commit()
    await db.refresh(current_user)
    
    logger.info(f"Regenerated API key for user {current_user.email}")
    
    return {
        "message": "API key regenerated successfully",
        "api_key": api_key,
        "warning": "Save this key securely - it will not be shown again!"
    }
