"""Rate limiting middleware using Redis."""

from typing import Callable
import time
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import redis.asyncio as aioredis
from loguru import logger

from app.core.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using Redis sliding window algorithm.
    
    Tracks requests per IP address with configurable limits:
    - Per minute limit
    - Per hour limit
    """
    
    _redis_client = None
    
    @classmethod
    async def get_redis(cls):
        """Get or create Redis connection."""
        if cls._redis_client is None:
            try:
                cls._redis_client = await aioredis.from_url(
                    settings.redis_url,
                    password=settings.redis_password,
                    encoding="utf-8",
                    decode_responses=True
                )
                logger.info("Redis connection established for rate limiting")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                raise
        return cls._redis_client
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Process request with rate limiting."""
        
        # Skip rate limiting for health checks and static files
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        try:
            redis = await self.get_redis()
            
            # Check rate limits
            await self._check_rate_limit(redis, client_ip, request.url.path)
            
            # Process request
            response = await call_next(request)
            
            # Add rate  limit headers
            response.headers["X-RateLimit-Limit-Minute"] = str(settings.rate_limit_per_minute)
            response.headers["X-RateLimit-Limit-Hour"] = str(settings.rate_limit_per_hour)
            
            return response
            
        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail},
                headers=e.headers
            )
        except Exception as e:
            logger.error(f"Rate limit error: {e}")
            # On error, allow request to proceed
            return await call_next(request)
    
    async def _check_rate_limit(self, redis: aioredis.Redis, client_ip: str, path: str):
        """
        Check if request exceeds rate limits.
        
        Args:
            redis: Redis client
            client_ip: Client IP address
            path: Request path
            
        Raises:
            HTTPException: If rate limit exceeded
        """
        current_time = int(time.time())
        
        # Per-minute check
        minute_key = f"ratelimit:{client_ip}:minute:{current_time // 60}"
        minute_count = await redis.incr(minute_key)
        
        if minute_count == 1:
            await redis.expire(minute_key, 60)
        
        if minute_count > settings.rate_limit_per_minute:
            logger.warning(f"Rate limit exceeded (minute): {client_ip} - {path}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests per minute. Please slow down.",
                headers={"Retry-After": "60"}
            )
        
        # Per-hour check
        hour_key = f"ratelimit:{client_ip}:hour:{current_time // 3600}"
        hour_count = await redis.incr(hour_key)
        
        if hour_count == 1:
            await redis.expire(hour_key, 3600)
        
        if hour_count > settings.rate_limit_per_hour:
            logger.warning(f"Rate limit exceeded (hour): {client_ip} - {path}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests per hour. Please try again later.",
                headers={"Retry-After": "3600"}
            )
    
    @classmethod
    async def close(cls):
        """Close Redis connection."""
        if cls._redis_client is not None:
            await cls._redis_client.close()
            cls._redis_client = None
            logger.info("Redis connection closed")
