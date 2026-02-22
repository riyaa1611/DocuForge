"""Tests for schedules endpoints."""

import pytest
from uuid import uuid4
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_schedule(test_client: AsyncClient, auth_headers, test_template):
    """Test schedule creation."""
    response = await test_client.post(
        "/api/v1/schedules",
        headers=auth_headers,
        json={
            "name": "Daily Report",
            "template_id": str(test_template.id),
            "cron_expression": "0 8 * * *",
        },
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Daily Report"
    assert data["cron_expression"] == "0 8 * * *"
    assert data["is_active"] is True
    assert "next_run" in data


@pytest.mark.asyncio
async def test_create_schedule_invalid_cron(test_client: AsyncClient, auth_headers, test_template):
    """Test schedule creation with invalid cron."""
    response = await test_client.post(
        "/api/v1/schedules",
        headers=auth_headers,
        json={
            "name": "Invalid Schedule",
            "template_id": str(test_template.id),
            "cron_expression": "invalid cron",
        },
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_schedules(test_client: AsyncClient, auth_headers):
    """Test listing schedules."""
    response = await test_client.get(
        "/api/v1/schedules",
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
