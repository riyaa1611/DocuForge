"""
DocuForge - FastAPI Application

A production-ready backend for automated PDF report generation with scheduling.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

from app.core.config import settings
from app.core.database import init_db, close_db
from app.core.rate_limit import RateLimitMiddleware
from app.api.routes import (
    auth_router,
    reports_router,
    templates_router,
    schedules_router,
)
from app.api.routes.api_keys import router as api_keys_router
from app.api.routes.websocket import router as websocket_router
from app.services.scheduler import SchedulerService
from app.services.pdf_generator import PDFGenerator


# Configure loguru
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.log_level,
)
logger.add(
    "logs/app.log",
    rotation="10 MB",
    retention="7 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting DocuForge...")

    # Initialize database
    await init_db()
    logger.info("Database initialized")

    # Seed default templates
    await seed_templates()

    # Start scheduler
    SchedulerService.start()
    logger.info("Scheduler started")

    # Load existing schedules into scheduler
    await load_schedules()

    logger.info("DocuForge started successfully!")

    yield

    # Shutdown
    logger.info("Shutting down DocuForge...")

    # Stop scheduler
    SchedulerService.shutdown()

    # Close browser
    await PDFGenerator.close_browser()

    # Close database
    await close_db()

    logger.info("DocuForge stopped.")


async def seed_templates():
    """Seed default templates into the database."""
    from app.core.database import async_session_factory
    from app.models.template import Template
    from sqlalchemy import select

    templates_data = [
        {
            "name": "financial_report.html",
            "description": "Financial report with revenue, expenses, and key metrics",
            "html_path": "financial_report.html",
            "schema": {
                "company_name": "string",
                "period": "string",
                "revenue": "number",
                "expenses": "number",
                "net_income": "number",
                "metrics": "array of {name, value, change}",
            },
        },
        {
            "name": "invoice.html",
            "description": "Professional invoice with line items and totals",
            "html_path": "invoice.html",
            "schema": {
                "invoice_number": "string",
                "invoice_date": "string",
                "due_date": "string",
                "company": "{name, address, city, email}",
                "client": "{name, address, city, email}",
                "items": "array of {description, quantity, rate, amount}",
                "subtotal": "number",
                "tax_rate": "number",
                "total": "number",
            },
        },
        {
            "name": "sales_summary.html",
            "description": "Sales summary with metrics, regional breakdown, and top products",
            "html_path": "sales_summary.html",
            "schema": {
                "report_title": "string",
                "report_date": "string",
                "total_sales": "number",
                "total_orders": "number",
                "average_order": "number",
                "sales_by_region": "{labels: array, values: array}",
                "top_products": "array of {name, units, revenue}",
            },
        },
    ]

    async with async_session_factory() as session:
        for data in templates_data:
            # Check if template exists
            result = await session.execute(
                select(Template).where(Template.name == data["name"])
            )
            if not result.scalar_one_or_none():
                template = Template(**data)
                session.add(template)
                logger.info(f"Seeded template: {data['name']}")

        await session.commit()


async def load_schedules():
    """Load existing active schedules into the scheduler."""
    from app.core.database import async_session_factory
    from app.models.schedule import Schedule
    from app.api.routes.schedules import execute_scheduled_report
    from sqlalchemy import select

    async with async_session_factory() as session:
        result = await session.execute(
            select(Schedule).where(Schedule.is_active == True)
        )
        schedules = result.scalars().all()

        for schedule in schedules:
            try:
                SchedulerService.add_job(
                    job_id=str(schedule.id),
                    func=execute_scheduled_report,
                    cron_expression=schedule.cron_expression,
                    args=(schedule.id,),
                )
            except Exception as e:
                logger.error(f"Failed to load schedule {schedule.id}: {e}")

        logger.info(f"Loaded {len(schedules)} schedules")


# Create FastAPI app
app = FastAPI(
    title="DocuForge",
    description="""
    A production-ready API for automated PDF report generation with scheduling.
    
    ## Features
    - **Authentication**: JWT-based auth with access and refresh tokens
    - **Report Generation**: Generate PDFs from HTML templates with dynamic data
    - **Charts**: Automatic chart generation (bar, line, pie) using Matplotlib
    - **Scheduling**: Cron-based scheduling for recurring reports
    - **Multiple Data Sources**: SQL, REST APIs, CSV files
    
    ## Getting Started
    1. Register a user account
    2. Login to get access token
    3. List available templates
    4. Generate a report
    5. Download the PDF
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],  # Required for PDF downloads with filename
)

# Rate limiting middleware
try:
    app.add_middleware(RateLimitMiddleware)
    logger.info("Rate limiting middleware enabled")
except Exception as e:
    logger.warning(f"Rate limiting disabled: {e}")

# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")
app.include_router(templates_router, prefix="/api/v1")
app.include_router(schedules_router, prefix="/api/v1")
app.include_router(api_keys_router, prefix="/api/v1")
app.include_router(websocket_router)  # WebSocket doesn't need /api/v1 prefix


@app.get("/health", tags=["Health"])
@app.get(
    "/api/v1/health", tags=["Health"], include_in_schema=False
)  # Alias for frontend
async def health_check():
    """
    Health check endpoint.

    Returns the service status and version.
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "DocuForge",
    }


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint.

    Redirects to API documentation.
    """
    return {
        "message": "Welcome to DocuForge API",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
