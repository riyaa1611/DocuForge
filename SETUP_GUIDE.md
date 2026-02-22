# 🚀 Production Setup Guide

## 📋 Overview

This guide covers the complete setup of the PDF Report Generator for production deployment with all new features:

- ✅ Supabase removed (Pure FastAPI + PostgreSQL)
- ✅ Cloud storage (AWS S3 / MinIO)
- ✅ Rate limiting (Redis-based)
- ✅ Docker containerization
- ✅ CI/CD with GitHub Actions
- ✅ API key management
- ✅ WebSocket real-time updates

## 🔧 Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- PostgreSQL 16
- Redis 7
- (Optional) AWS Account for S3 or MinIO installation

## 📦 Environment Variables Setup

### Backend (.env)

**REQUIRED - You MUST set these:**

```bash
# Database - PostgreSQL connection
DATABASE_URL=postgresql+asyncpg://USERNAME:PASSWORD@HOST:PORT/DATABASE_NAME

# JWT Authentication - CHANGE THIS IN PRODUCTION!
# Generate with: openssl rand -hex 32
SECRET_KEY=your-super-secret-key-change-in-production
```

**Cloud Storage - Choose ONE backend:**

```bash
# Option 1: Local Storage (Development)
STORAGE_BACKEND=LOCAL
STORAGE_PATH=./storage

# Option 2: AWS S3 (Production)
STORAGE_BACKEND=S3
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_S3_BUCKET_NAME=pdf-reports-bucket
AWS_REGION=us-east-1

# Option 3: MinIO (Self-hosted S3-compatible)
STORAGE_BACKEND=MINIO
MINIO_ENDPOINT=http://localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=pdf-reports
MINIO_SECURE=false
```

**Redis - Required for rate limiting:**

```bash
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=  # Leave empty for no password

# Rate limits (adjust based on your needs)
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
```

**CORS - Update with your frontend URL:**

```bash
ALLOWED_ORIGINS=https://yourdomain.com,http://localhost:8080
```

**Optional Settings:**

```bash
# Email notifications
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
SMTP_FROM=noreply@yourapp.com

# Monitoring
SENTRY_DSN=your-sentry-dsn
ENVIRONMENT=production

# Server
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
```

### Frontend (.env)

**REQUIRED:**

```bash
VITE_API_URL=https://api.yourdomain.com/api/v1
VITE_WS_URL=wss://api.yourdomain.com/ws
```

**Optional:**

```bash
VITE_APP_NAME=PDF Report Generator
VITE_ENV=production
VITE_ENABLE_ANALYTICS=true
VITE_SENTRY_DSN=your-sentry-dsn
```

## 🐳 Docker Deployment

### Development

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production

```bash
# Copy and edit environment files
cp pdf-report-generator/.env.example pdf-report-generator/.env
cp frontend/.env.example frontend/.env

# Edit .env files with production values
nano pdf-report-generator/.env
nano frontend/.env

# Build and start production containers
docker-compose -f pdf-report-generator/docker-compose.prod.yml up -d

# Check status
docker-compose -f pdf-report-generator/docker-compose.prod.yml ps
```

## 📝 Manual Installation

### Backend

```bash
cd pdf-report-generator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser
playwright install chromium

# Create .env from example
cp .env.example .env
# Edit .env with your values

# Start PostgreSQL and Redis (Docker)
docker-compose up -d postgres redis

# Run migrations (tables auto-create on first run)
# Start server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install
# or
bun install

# Create .env from example
cp .env.example .env
# Edit .env with your values

# Development
npm run dev

# Production build
npm run build
npm run preview

# Or serve with nginx (see Dockerfile)
```

## ☁️ Cloud Storage Setup

### AWS S3

1. Create S3 bucket in AWS Console
2. Create IAM user with S3 access
3. Generate access keys
4. Set environment variables:
   ```bash
   STORAGE_BACKEND=S3
   AWS_ACCESS_KEY_ID=your-key
   AWS_SECRET_ACCESS_KEY=your-secret
   AWS_S3_BUCKET_NAME=your-bucket
   AWS_REGION=us-east-1
   ```

### MinIO (Self-hosted)

```bash
# Start MinIO with Docker
docker run -d \
  -p 9000:9000 \
  -p 9001:9001 \
  --name minio \
  -e "MINIO_ROOT_USER=minioadmin" \
  -e "MINIO_ROOT_PASSWORD=minioadmin" \
  minio/minio server /data --console-address ":9001"

# Access console at http://localhost:9001
# Create bucket named "pdf-reports"

# Set environment variables:
STORAGE_BACKEND=MINIO
MINIO_ENDPOINT=http://localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=pdf-reports
```

## 🔐 Security Checklist

- [ ] Change `SECRET_KEY` to a random 32-byte hex string
- [ ] Use strong database passwords
- [ ] Enable Redis password authentication
- [ ] Configure CORS with specific origins
- [ ] Use HTTPS in production
- [ ] Keep API keys secure
- [ ] Rotate credentials regularly
- [ ] Enable rate limiting
- [ ] Set up monitoring and logging
- [ ] Regular database backups

## 🧪 Testing

```bash
# Backend tests
cd pdf-report-generator
pytest tests/ -v

# Frontend tests
cd frontend
npm test

# E2E tests (add your tests)
```

## 📊 Monitoring

### Health Checks

- Backend: `https://api.yourdomain.com/health`
- Frontend: `https://yourdomain.com/health`

### Logs

```bash
# Docker logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Application logs
tail -f pdf-report-generator/logs/app.log
```

## 🚀 CI/CD Setup

The project includes GitHub Actions workflow (`.github/workflows/ci-cd.yml`).

**Required GitHub Secrets:**

- `GITHUB_TOKEN` (automatic)
- Add deployment-specific secrets based on your platform

**Workflow triggers:**
- Push to `main`: Full build, test, and deploy
- Push to `develop`: Build and test only
- Pull requests: Test only

## 🔄 Database Migrations

Tables are auto-created on first run. For schema changes:

```bash
# Using Alembic (future enhancement)
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## 📱 API Key Management

Users can generate API keys via:
1. Dashboard UI (`/dashboard`)
2. API endpoint: `POST /api/v1/api-keys/generate`

API usage:
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.yourdomain.com/api/v1/templates
```

## 🌐 WebSocket Real-time Updates

Connect to WebSocket:
```javascript
const ws = new WebSocket('wss://api.yourdomain.com/ws?token=YOUR_TOKEN');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Update:', data);
};
```

## 🆘 Troubleshooting

### Backend won't start
- Check PostgreSQL is running: `docker ps`
- Verify DATABASE_URL is correct
- Check logs: `docker-compose logs backend`

### Redis connection fails
- Ensure Redis is running: `docker ps | grep redis`
- Check REDIS_URL environment variable
- Rate limiting will be disabled if Redis fails

### Cloud storage errors
- Verify credentials are correct
- Check bucket exists and has proper permissions
- Test with LOCAL storage first

### Frontend can't connect to backend
- Check VITE_API_URL is correct
- Verify CORS settings in backend
- Check network/firewall rules

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/docs/)
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [MinIO Documentation](https://min.io/docs/)

## 🎉 You're Ready!

Your PDF Report Generator is now production-ready with:
- ✅ Cloud storage
- ✅ Rate limiting
- ✅ API key management
- ✅ Real-time WebSocket updates
- ✅ Docker containerization
- ✅ CI/CD pipeline

For questions or issues, check the logs and documentation above.
