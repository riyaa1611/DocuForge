"""User-related Pydantic schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Schema for user registration."""
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="User full name")
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="User password (min 8 characters)"
    )


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class UserResponse(BaseModel):
    """Schema for user response."""
    id: UUID
    name: Optional[str] = None
    email: str
    api_key: Optional[str] = None
    created_at: datetime
    
    model_config = {"from_attributes": True}


class Token(BaseModel):
    """Schema for authentication tokens."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")


class TokenRefresh(BaseModel):
    """Schema for token refresh request."""
    refresh_token: str = Field(..., description="JWT refresh token")


class TokenData(BaseModel):
    """Schema for decoded token data."""
    user_id: Optional[UUID] = None
    email: Optional[str] = None
    token_type: Optional[str] = None
