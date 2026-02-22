"""Authentication endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.api.dependencies import get_db, get_current_user
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_api_key,
)
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    TokenRefresh,
)


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user account.

    - **email**: Valid email address (must be unique)
    - **password**: Password (minimum 8 characters)
    """
    # Normalize email to lowercase
    user_data.email = user_data.email.lower()

    # Check if email already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create user
    user = User(
        email=user_data.email,
        name=user_data.name,
        hashed_password=hash_password(user_data.password),
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    logger.info(f"User registered: {user.email}")
    return user


@router.post(
    "/login",
    response_model=Token,
    summary="Login to get access token",
)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate a user and return access and refresh tokens.

    - **email**: User's email address
    - **password**: User's password
    """
    logger.info(f"Login attempt for email: {credentials.email}")

    # Normalize email to lowercase
    credentials.email = credentials.email.lower()

    # Get user
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()

    if not user:
        logger.warning(f"Login failed: User {credentials.email} not found in DB.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(credentials.password, user.hashed_password):
        logger.warning(f"Login failed: Password mismatch for user {credentials.email}.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    logger.info(f"User logged in: {user.email}")

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post(
    "/refresh",
    response_model=Token,
    summary="Refresh access token",
)
async def refresh_token(
    token_data: TokenRefresh,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a new access token using a refresh token.
    """
    payload = decode_token(token_data.refresh_token)

    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    # Verify user exists
    from uuid import UUID

    user = await db.get(User, UUID(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # Create new tokens
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user info",
)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    """
    Get the current authenticated user's information.
    """
    return current_user


@router.post(
    "/api-key",
    response_model=dict,
    summary="Generate API key",
)
async def generate_user_api_key(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a new API key for the current user.
    The old API key will be replaced.
    """
    api_key = generate_api_key()
    current_user.api_key = api_key
    await db.commit()

    logger.info(f"API key generated for user: {current_user.email}")

    return {"api_key": api_key}
