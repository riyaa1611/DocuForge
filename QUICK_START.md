# 🚀 Quick Start - What You Need to Do Manually

## ⚡ Immediate Action Required

### 1. Backend Environment Setup (5 minutes)

```bash
cd pdf-report-generator

# Copy template
cp .env.example .env

# Edit .env and add these REQUIRED values:
```

**REQUIRED Variables (add to .env):**
```bash
# Database - Use your PostgreSQL connection
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/pdf_reports

# Security - CRITICAL: Generate a new secret key!
SECRET_KEY=replace_with_output_from_command_below

# Redis - For rate limiting
REDIS_URL=redis://localhost:6379/0

# Storage - Start with LOCAL for development
STORAGE_BACKEND=LOCAL
STORAGE_PATH=./storage

# CORS - Update with your frontend URL
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

**Generate SECRET_KEY (run this command):**
```bash
# Linux/Mac:
openssl rand -hex 32

# Windows PowerShell:
python -c "import secrets; print(secrets.token_hex(32))"

# Copy the output and paste as SECRET_KEY value
```

### 2. Frontend Environment Setup (1 minute)

```bash
cd frontend

# Copy template
cp .env.example .env

# Edit .env and add:
```

**REQUIRED Variables (add to .env):**
```bash
VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws
```

### 3. Install Dependencies

**Backend:**
```bash
cd pdf-report-generator
pip install -r requirements.txt
playwright install chromium
```

**Frontend:**
```bash
cd frontend
npm install
# or: bun install
```

### 4. Start Services with Docker

**Option A: Use Docker Compose (Recommended)**
```bash
# Start PostgreSQL, Redis, MinIO
docker-compose up -d postgres redis minio

# Start backend manually (for development)
cd pdf-report-generator
uvicorn app.main:app --reload

# Start frontend manually
cd frontend
npm run dev
```

**Option B: Use Docker for Everything**
```bash
# Start entire stack
docker-compose up -d

# View logs
docker-compose logs -f

# Access:
# Frontend: http://localhost:5173
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### 5. Verify Installation

Open your browser:
- **Frontend**: http://localhost:5173
- **Backend API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 📝 Optional: Production Configuration

### For AWS S3 Storage (Production):

Add to `pdf-report-generator/.env`:
```bash
STORAGE_BACKEND=S3
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_S3_BUCKET_NAME=your-bucket-name
AWS_REGION=us-east-1
```

### For MinIO Storage (Self-hosted):

Add to `pdf-report-generator/.env`:
```bash
STORAGE_BACKEND=MINIO
MINIO_ENDPOINT=http://localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=pdf-reports
MINIO_SECURE=false
```

### Enable Email Notifications:

Add to `pdf-report-generator/.env`:
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@yourapp.com
SMTP_FROM_NAME=DocuForge
```

---

## 🔥 Common Issues & Solutions

### Issue 1: "Database connection failed"
**Solution:** Make sure PostgreSQL is running
```bash
docker-compose up -d postgres
# Or install PostgreSQL locally
```

### Issue 2: "Redis connection failed"
**Solution:** Start Redis or disable rate limiting temporarily
```bash
docker-compose up -d redis
# Or comment out rate limiting in app/main.py
```

### Issue 3: "Playwright browser not found"
**Solution:** Install Chromium
```bash
playwright install chromium
```

### Issue 4: "CORS error in browser"
**Solution:** Update ALLOWED_ORIGINS in backend .env
```bash
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Issue 5: "Module not found" errors
**Solution:** Reinstall dependencies
```bash
# Backend
pip install -r requirements.txt --upgrade

# Frontend
rm -rf node_modules package-lock.json
npm install
```

---

## 📚 Documentation Reference

For detailed information, see these files:

1. **ENV_VARIABLES.md** - All environment variables explained
2. **SETUP_GUIDE.md** - Complete deployment guide
3. **CHANGES_SUMMARY.md** - All implemented features
4. **Backend API**: http://localhost:8000/docs (after starting)

---

## ✅ Checklist - Did You Do These?

**Backend:**
- [ ] Copied `.env.example` to `.env` in `pdf-report-generator/`
- [ ] Set `DATABASE_URL` to your PostgreSQL connection
- [ ] Generated and set new `SECRET_KEY` using openssl/python
- [ ] Set `REDIS_URL` (or started Redis with Docker)
- [ ] Chose `STORAGE_BACKEND` (LOCAL for dev, S3/MINIO for prod)
- [ ] Updated `ALLOWED_ORIGINS` with your frontend URL
- [ ] Ran `pip install -r requirements.txt`
- [ ] Ran `playwright install chromium`
- [ ] Started PostgreSQL (via Docker or locally)
- [ ] Started backend: `uvicorn app.main:app --reload`

**Frontend:**
- [ ] Copied `.env.example` to `.env` in `frontend/`
- [ ] Set `VITE_API_URL=http://localhost:8000/api/v1`
- [ ] Set `VITE_WS_URL=ws://localhost:8000/ws`
- [ ] Ran `npm install` or `bun install`
- [ ] Started frontend: `npm run dev`

**Access:**
- [ ] Can access frontend at http://localhost:5173
- [ ] Can access API docs at http://localhost:8000/docs
- [ ] Can register/login successfully
- [ ] Can generate a PDF report

---

## 🎯 Minimal Quick Start (Just to Test)

If you just want to see it working quickly:

```bash
# 1. Start services
docker-compose up -d postgres redis

# 2. Backend .env (minimal)
cd pdf-report-generator
echo 'DATABASE_URL=postgresql+asyncpg://pdf_user:pdf_password@localhost:5432/pdf_reports
SECRET_KEY='$(python -c "import secrets; print(secrets.token_hex(32))")'
REDIS_URL=redis://localhost:6379/0
STORAGE_BACKEND=LOCAL
ALLOWED_ORIGINS=http://localhost:5173' > .env

# 3. Frontend .env (minimal)
cd ../frontend
echo 'VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws' > .env

# 4. Install & run
cd ../pdf-report-generator
pip install -r requirements.txt
playwright install chromium
uvicorn app.main:app --reload &

cd ../frontend
npm install
npm run dev
```

Then open http://localhost:5173 in your browser!

---

## 💡 Pro Tips

1. **Start with LOCAL storage** - Test everything works before S3
2. **Use Docker Compose** - Easiest way to run PostgreSQL + Redis
3. **Check logs** - If something fails, check console output
4. **Generate secure keys** - Never use example SECRET_KEY in production
5. **Read ENV_VARIABLES.md** - Has examples for every setting

---

**Need help?** Check the troubleshooting sections in SETUP_GUIDE.md and ENV_VARIABLES.md!
