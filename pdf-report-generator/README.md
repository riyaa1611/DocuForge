# DocuForge

A production-ready FastAPI backend for automated PDF report generation with scheduling capabilities.

## Features

- **JWT Authentication**: Secure user registration, login, and API key support
- **PDF Generation**: Convert HTML templates to professional PDFs using Playwright
- **Chart Generation**: Automatic chart creation (bar, line, pie) using Matplotlib
- **Multiple Templates**: Financial reports, invoices, sales summaries
- **Scheduling**: Cron-based scheduling for recurring reports with APScheduler
- **Multi-source Data**: Fetch data from SQL, REST APIs, or CSV files
- **Background Processing**: Async report generation with status tracking

## Tech Stack

- **Framework**: FastAPI + Uvicorn
- **Database**: PostgreSQL (async with SQLAlchemy 2.0)
- **PDF Engine**: Playwright (Chromium headless)
- **Charts**: Matplotlib
- **Scheduling**: APScheduler
- **Auth**: JWT (python-jose) + bcrypt

## Quick Start

### 1. Prerequisites

- Python 3.11+
- Docker (for PostgreSQL)
- Node.js (for Playwright)

### 2. Setup

```bash
# Clone and enter directory
cd pdf-report-generator

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser
playwright install chromium

# Start PostgreSQL
docker-compose up -d

# Run the server
uvicorn app.main:app --reload
```

### 3. Access the API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login, get tokens |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| GET | `/api/v1/auth/me` | Get current user |

### Reports
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/reports/generate` | Generate report (async) |
| GET | `/api/v1/reports` | List reports |
| GET | `/api/v1/reports/{id}` | Get report details |
| GET | `/api/v1/reports/{id}/status` | Check generation status |
| GET | `/api/v1/reports/{id}/download` | Download PDF |
| DELETE | `/api/v1/reports/{id}` | Delete report |

### Templates
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/templates` | List templates |
| GET | `/api/v1/templates/{id}` | Get template details |

### Schedules
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/schedules` | Create schedule |
| GET | `/api/v1/schedules` | List schedules |
| PUT | `/api/v1/schedules/{id}` | Update schedule |
| DELETE | `/api/v1/schedules/{id}` | Delete schedule |

## Usage Example

```python
import httpx

# Register
response = httpx.post("http://localhost:8000/api/v1/auth/register", json={
    "email": "user@example.com",
    "password": "securepassword123"
})

# Login
response = httpx.post("http://localhost:8000/api/v1/auth/login", json={
    "email": "user@example.com",
    "password": "securepassword123"
})
token = response.json()["access_token"]

# Get templates
headers = {"Authorization": f"Bearer {token}"}
templates = httpx.get("http://localhost:8000/api/v1/templates", headers=headers)
template_id = templates.json()[0]["id"]

# Generate report
response = httpx.post(
    "http://localhost:8000/api/v1/reports/generate",
    headers=headers,
    json={"template_id": template_id}
)
job_id = response.json()["job_id"]

# Check status
status = httpx.get(f"http://localhost:8000/api/v1/reports/{job_id}/status", headers=headers)

# Download PDF (when completed)
pdf = httpx.get(f"http://localhost:8000/api/v1/reports/{job_id}/download", headers=headers)
with open("report.pdf", "wb") as f:
    f.write(pdf.content)
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://...` | PostgreSQL connection |
| `SECRET_KEY` | - | JWT signing key |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token lifetime |
| `STORAGE_PATH` | `./storage` | PDF storage directory |
| `ALLOWED_ORIGINS` | `http://localhost:5173` | CORS origins |

## Project Structure

```
pdf-report-generator/
├── app/
│   ├── api/
│   │   ├── dependencies.py    # Auth & DB dependencies
│   │   └── routes/            # API route handlers
│   ├── core/
│   │   ├── config.py          # Settings
│   │   ├── database.py        # SQLAlchemy setup
│   │   └── security.py        # JWT & password utils
│   ├── models/                # SQLAlchemy models
│   ├── schemas/               # Pydantic schemas
│   ├── services/              # Business logic
│   │   ├── pdf_generator.py   # Playwright PDF
│   │   ├── chart_generator.py # Matplotlib charts
│   │   └── scheduler.py       # APScheduler
│   ├── templates/             # HTML templates
│   └── main.py                # FastAPI app
├── storage/                   # Generated PDFs
├── tests/                     # Test suite
├── docker-compose.yml         # PostgreSQL
└── requirements.txt
```

## License

MIT
