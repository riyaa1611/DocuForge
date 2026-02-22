# ============================================
# Multi-stage Dockerfile for FastAPI Backend
# ============================================

FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*


# ============================================
# Builder stage - Install Python dependencies
# ============================================
FROM base as builder

COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Install Playwright and Chromium
RUN pip install --user playwright && \
    python -m playwright install chromium && \
    python -m playwright install-deps chromium


# ============================================
# Production stage
# ============================================
FROM base as production

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local
COPY --from=builder /root/.cache/ms-playwright /root/.cache/ms-playwright

# Update PATH
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY app /app/app

# Create storage directories
RUN mkdir -p /app/storage/reports /app/storage/temp /app/logs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health')" || exit 1

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


# ============================================
# Development stage
# ============================================
FROM production as development

# Install development dependencies
RUN pip install --user \
    pytest \
    pytest-asyncio \
    pytest-cov \
    ipython \
    black \
    ruff

# Run with hot reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
