"""Tests for authentication endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(test_client: AsyncClient):
    """Test user registration."""
    response = await test_client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "securepassword123",
        },
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(test_client: AsyncClient, test_user):
    """Test registration with duplicate email."""
    response = await test_client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "anotherpassword",
        },
    )
    
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_success(test_client: AsyncClient, test_user):
    """Test successful login."""
    response = await test_client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(test_client: AsyncClient, test_user):
    """Test login with wrong password."""
    response = await test_client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "wrongpassword",
        },
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(test_client: AsyncClient):
    """Test login with non-existent user."""
    response = await test_client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "somepassword",
        },
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me(test_client: AsyncClient, auth_headers):
    """Test getting current user info."""
    response = await test_client.get(
        "/api/v1/auth/me",
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_get_me_unauthorized(test_client: AsyncClient):
    """Test getting current user without auth."""
    response = await test_client.get("/api/v1/auth/me")
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_refresh_token(test_client: AsyncClient, test_user):
    """Test refreshing access token."""
    # First login to get tokens
    login_response = await test_client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
        },
    )
    refresh_token = login_response.json()["refresh_token"]
    
    # Refresh
    response = await test_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
