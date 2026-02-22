# 📝 Environment Variables Reference

## Quick Start - Minimal Required Variables

### Backend (Minimum to run)
```bash
DATABASE_URL=postgresql+asyncpg://pdfgen:pdfgen123@localhost:5432/pdfgen_db
SECRET_KEY=your-secret-key-here  # CHANGE IN PRODUCTION!
REDIS_URL=redis://localhost:6379/0
```

### Frontend (Minimum to run)
```bash
VITE_API_URL=http://localhost:8000/api/v1
```

---

## Complete Backend Environment Variables

### 🗄️ Database Configuration
```bash
# PostgreSQL async connection string
# Format: postgresql+asyncpg://USER:PASSWORD@HOST:PORT/DATABASE
DATABASE_URL=postgresql+asyncpg://pdfgen:pdfgen123@localhost:5432/pdfgen_db
```

### 🔐 JWT Authentication
```bash
# Secret key for JWT signing (MUST CHANGE IN PRODUCTION!)
# Generate with: openssl rand -hex 32
SECRET_KEY=your-super-secret-key-change-in-production

# JWT algorithm (default: HS256)
ALGORITHM=HS256

# Token expiration times
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 💾 Storage Configuration
```bash
# Storage backend: LOCAL, S3, or MINIO
STORAGE_BACKEND=LOCAL

# Local storage path (used when STORAGE_BACKEND=LOCAL)
STORAGE_PATH=./storage
```

### ☁️ AWS S3 Configuration
```bash
# Only needed if STORAGE_BACKEND=S3
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_S3_BUCKET_NAME=pdf-reports-bucket
AWS_REGION=us-east-1
```

### 🗃️ MinIO Configuration
```bash
# Only needed if STORAGE_BACKEND=MINIO
MINIO_ENDPOINT=http://localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=pdf-reports
MINIO_SECURE=false  # true for HTTPS
```

### 🔴 Redis Configuration
```bash
# Redis connection URL
REDIS_URL=redis://localhost:6379/0

# Redis password (leave empty if no auth)
REDIS_PASSWORD=
```

### 🚦 Rate Limiting
```bash
# Maximum requests per minute per IP
RATE_LIMIT_PER_MINUTE=60

# Maximum requests per hour per IP
RATE_LIMIT_PER_HOUR=1000
```

### 🌐 CORS Configuration
```bash
# Comma-separated list of allowed origins
# Add your frontend URL here!
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost:8080
```

### 🖥️ Server Configuration
```bash
# Server host (0.0.0.0 = all interfaces)
HOST=0.0.0.0

# Server port
PORT=8000

# Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# Environment name
ENVIRONMENT=development  # or production, staging
```

### 📧 Email Configuration (Optional)
```bash
# SMTP server settings for email notifications
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
SMTP_FROM=noreply@yourapp.com
```

### 🔄 Celery/Background Tasks (Optional)
```bash
# Redis URLs for Celery (if using Celery instead of APScheduler)
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
```

### 📊 Monitoring (Optional)
```bash
# Sentry DSN for error tracking
SENTRY_DSN=
```

---

## Complete Frontend Environment Variables

### 🌐 API Configuration
```bash
# Backend API base URL
VITE_API_URL=http://localhost:8000/api/v1

# WebSocket URL for real-time updates
VITE_WS_URL=ws://localhost:8000/ws
```

### 🎨 Application Configuration
```bash
# Application name
VITE_APP_NAME=PDF Report Generator

# Application version
VITE_APP_VERSION=1.0.0

# Environment
VITE_ENV=development  # or production, staging
```

### 🔧 Feature Flags
```bash
# Enable analytics
VITE_ENABLE_ANALYTICS=false

# Enable error reporting
VITE_ENABLE_ERROR_REPORTING=false
```

### 📊 External Services (Optional)
```bash
# Sentry DSN for frontend error tracking
VITE_SENTRY_DSN=

# Google Analytics ID
VITE_GOOGLE_ANALYTICS_ID=
```

### 🎨 Theme Configuration
```bash
# Default theme: system, light, or dark
VITE_DEFAULT_THEME=system
```

---

## 🚨 Important Security Notes

1. **SECRET_KEY**: NEVER use the default in production! Generate a secure one:
   ```bash
   openssl rand -hex 32
   ```

2. **Database Credentials**: Use strong passwords in production

3. **Redis Password**: Enable password authentication in production:
   ```bash
   redis-server --requirepass your-password
   REDIS_URL=redis://:your-password@localhost:6379/0
   ```

4. **CORS Origins**: Only list trusted domains:
   ```bash
   ALLOWED_ORIGINS=https://yourdomain.com
   ```

5. **Cloud Storage Keys**: Keep AWS/MinIO keys secure, never commit to git

6. **Environment Files**: Add `.env` to `.gitignore` (already done)

---

## 🔍 Finding Your Values

### Database URL
```bash
# Local PostgreSQL
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/database_name

# Docker PostgreSQL
DATABASE_URL=postgresql+asyncpg://pdfgen:pdfgen123@postgres:5432/pdfgen_db

# External PostgreSQL (e.g., AWS RDS)
DATABASE_URL=postgresql+asyncpg://user:pass@rds-instance.region.rds.amazonaws.com:5432/dbname
```

### Redis URL
```bash
# Local Redis
REDIS_URL=redis://localhost:6379/0

# Docker Redis
REDIS_URL=redis://redis:6379/0

# Redis with password
REDIS_URL=redis://:password@localhost:6379/0

# External Redis (e.g., AWS ElastiCache)
REDIS_URL=redis://cache-instance.region.cache.amazonaws.com:6379/0
```

### Storage Backend Choice

| Backend | Use Case | Cost | Scalability |
|---------|----------|------|-------------|
| LOCAL | Development, small deployments | Free | Limited |
| S3 | Production, high reliability | Pay-per-use | Unlimited |
| MinIO | Self-hosted production | Infrastructure cost | High |

---

## 📋 Production Checklist

Before deploying to production, ensure you have:

**Backend:**
- [ ] Set unique `SECRET_KEY`
- [ ] Configure `DATABASE_URL` with production DB
- [ ] Set `REDIS_URL` to production Redis
- [ ] Choose and configure `STORAGE_BACKEND` (S3 or MinIO)
- [ ] Update `ALLOWED_ORIGINS` with production frontend URL
- [ ] Set `ENVIRONMENT=production`
- [ ] Configure `SMTP_*` for email notifications (optional)
- [ ] Set up `SENTRY_DSN` for error tracking (optional)

**Frontend:**
- [ ] Set `VITE_API_URL` to production backend URL
- [ ] Set `VITE_WS_URL` to production WebSocket URL
- [ ] Set `VITE_ENV=production`
- [ ] Configure analytics if needed

**Infrastructure:**
- [ ] PostgreSQL database running and accessible
- [ ] Redis instance running and accessible
- [ ] S3 bucket created or MinIO installed
- [ ] SSL certificates configured (HTTPS)
- [ ] Firewall rules configured
- [ ] Backup strategy in place

---

## 🆘 Troubleshooting

### "Database connection failed"
- Check `DATABASE_URL` format
- Verify PostgreSQL is running
- Test connection: `psql $DATABASE_URL`

### "Redis connection error"
- Check `REDIS_URL` format
- Verify Redis is running: `redis-cli ping`
- Check Redis password if configured

### "Storage upload failed"
- Verify cloud credentials
- Check bucket/container exists
- Test with `STORAGE_BACKEND=LOCAL` first

### "CORS error"
- Add frontend URL to `ALLOWED_ORIGINS`
- Check protocol (http vs https)
- Verify no trailing slashes

---

## 📚 Additional Help

- Copy `.env.example` files to `.env` and customize
- Check `SETUP_GUIDE.md` for detailed setup instructions
- See Docker Compose files for container configuration
- Review application logs for specific error messages

Need more help? Check the logs:
```bash
# Backend logs
tail -f pdf-report-generator/logs/app.log

# Docker container logs
docker-compose logs -f backend
```
