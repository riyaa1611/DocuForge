"""Tests for reports endpoints."""

import pytest
from uuid import uuid4
from httpx import AsyncClient
from unittest.mock import patch


@pytest.mark.asyncio
async def test_generate_report(test_client: AsyncClient, auth_headers, test_template):
    """Test report generation."""
    with patch("app.api.routes.reports.process_report_background"):
        response = await test_client.post(
            "/api/v1/reports/generate",
            headers=auth_headers,
            json={"template_id": str(test_template.id)},
        )
    
    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_generate_report_invalid_template(test_client: AsyncClient, auth_headers):
    """Test report generation with invalid template."""
    response = await test_client.post(
        "/api/v1/reports/generate",
        headers=auth_headers,
        json={"template_id": str(uuid4())},
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_reports(test_client: AsyncClient, auth_headers):
    """Test listing reports."""
    response = await test_client.get(
        "/api/v1/reports",
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data


@pytest.mark.asyncio
async def test_list_reports_unauthorized(test_client: AsyncClient):
    """Test listing reports without auth."""
    response = await test_client.get("/api/v1/reports")
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_report_not_found(test_client: AsyncClient, auth_headers):
    """Test getting non-existent report."""
    response = await test_client.get(
        f"/api/v1/reports/{uuid4()}",
        headers=auth_headers,
    )
    
    assert response.status_code == 404
