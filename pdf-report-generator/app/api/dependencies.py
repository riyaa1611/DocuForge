"""API dependencies for authentication and database access."""

from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.core.security import decode_token
from app.models.user import User


# Security scheme
security = HTTPBearer()


async def get_db() -> AsyncSession:
    """
    Dependency that provides an async database session.

    Usage:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Dependency that validates JWT token and returns the current user.

    Raises:
        HTTPException 401: If token is invalid or expired
        HTTPException 401: If user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise credentials_exception

    # Check token type
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise credentials_exception

    # Get user from database
    user = await db.get(User, user_uuid)
    if user is None:
        raise credentials_exception

    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """
    Optional authentication dependency.
    Returns None if no valid token is provided.
    """
    if credentials is None:
        return None

    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None


async def verify_api_key(
    api_key: str,
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Verify API key and return the associated user.

    Usage:
        @router.get("/items")
        async def get_items(
            api_key: str = Header(..., alias="X-API-Key"),
            db: AsyncSession = Depends(get_db)
        ):
            user = await verify_api_key(api_key, db)
            ...
    """
    result = await db.execute(select(User).where(User.api_key == api_key))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    return user


async def get_current_user_from_token(
    token: str,
    db: AsyncSession,
) -> Optional[User]:
    """
    Get user from JWT token string (for WebSocket authentication).
    Returns None if token is invalid.

    Args:
        token: JWT token string
        db: Database session

    Returns:
        User object or None if authentication fails
    """
    try:
        payload = decode_token(token)

        if payload is None:
            return None

        # Check token type
        if payload.get("type") != "access":
            return None

        user_id = payload.get("sub")
        if user_id is None:
            return None

        try:
            user_uuid = UUID(user_id)
        except ValueError:
            return None

        # Get user from database
        user = await db.get(User, user_uuid)
        return user

    except Exception as e:
        logger.error(f"Token validation failed: {e}")
        return None
