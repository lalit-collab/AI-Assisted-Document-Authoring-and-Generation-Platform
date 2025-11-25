# Deployment Guide

## Production Deployment Options

### 1. Heroku Deployment (Recommended for Quick Setup)

#### Prerequisites
- Heroku account and CLI installed
- PostgreSQL addon available

#### Steps

```bash
# Login to Heroku
heroku login

# Create new app
heroku create your-app-name

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:standard-0

# Set environment variables
heroku config:set \
  SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')" \
  GEMINI_API_KEY="your-gemini-key" \
  OPENAI_API_KEY="your-openai-key" \
  LLM_PROVIDER="gemini" \
  DEBUG="False" \
  ALLOWED_ORIGINS="https://your-domain.com"

# Deploy backend
git subtree push --prefix backend heroku main

# Deploy frontend (if separate app)
heroku create frontend-app-name --buildpack https://buildpack-registry.s3.amazonaws.com/buildpacks/heroku-community/static.tgz
npm run build
# Deploy dist/ folder
```

### 2. AWS Deployment (Elastic Beanstalk)

#### Steps

```bash
# Install EB CLI
pip install awsebcli

# Initialize EB
eb init -p python-3.9 ai-docgen

# Create environment
eb create production

# Deploy
eb deploy

# View logs
eb logs
```

**Frontend on CloudFront/S3:**
```bash
# Build frontend
npm run build

# Upload to S3
aws s3 sync dist/ s3://your-bucket-name/

# Set CloudFront distribution
# Enable CORS headers
```

### 3. Docker & Kubernetes (Enterprise)

#### Build Docker Image

**Dockerfile:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build & Push:**
```bash
docker build -t your-registry/docgen:latest .
docker push your-registry/docgen:latest

# Deploy with Kubernetes
kubectl apply -f k8s/deployment.yaml
```

### 4. DigitalOcean App Platform

1. Connect GitHub repo
2. Configure build commands:
   - Backend: `pip install -r requirements.txt`
   - Frontend: `npm install && npm run build`
3. Set environment variables
4. Deploy

---

## Environment Setup

### Production Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:pass@prod-db.c.amazonawsusercontent.com/docgen

# Security
DEBUG=False
SECRET_KEY=use-generated-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# LLM
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIza...
OPENAI_API_KEY=sk-...

# CORS
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Redis (optional)
REDIS_URL=redis://prod-redis:6379/0

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@yourdomain.com
SMTP_PASSWORD=app-password

# File Storage
EXPORT_TEMP_DIR=/var/exports
MAX_FILE_SIZE_MB=50
S3_BUCKET=your-bucket-name
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
```

---

## Pre-Deployment Checklist

- [ ] Database migrations tested
- [ ] All environment variables configured
- [ ] LLM API keys valid and quotas sufficient
- [ ] CORS origins updated
- [ ] SSL certificate configured
- [ ] Rate limiting configured
- [ ] Logging configured
- [ ] Monitoring alerts set up
- [ ] Backup strategy in place
- [ ] Disaster recovery plan
- [ ] Load testing completed
- [ ] Security audit passed

---

## Production Best Practices

### 1. Database
- Enable automated backups
- Set up replication for high availability
- Use connection pooling (PgBouncer)
- Monitor query performance

### 2. API Server
- Use Gunicorn with multiple workers
- Enable compression (gzip)
- Set up rate limiting
- Monitor response times

### 3. Frontend
- CDN distribution (CloudFront, Cloudflare)
- Minification and tree-shaking
- Service workers for offline support
- Cache busting with versioning

### 4. Monitoring & Logging
```python
# Backend logging setup
import logging
from pythonjsonlogger import jsonlogger

logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)
```

### 5. CI/CD Pipeline
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production
on:
  push:
    branches: [main]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: pytest tests/
      - name: Deploy
        run: |
          curl -X POST https://your-deployment-webhook
```

---

## Monitoring & Maintenance

### Health Checks
```bash
# Check API health
curl https://api.yourdomain.com/health

# Check database connection
curl https://api.yourdomain.com/api/docs
```

### Log Aggregation
```python
# Send logs to external service (e.g., Sentry, CloudWatch)
import sentry_sdk
sentry_sdk.init("your-sentry-dsn", traces_sample_rate=1.0)
```

### Performance Metrics
- Request latency: Target < 500ms
- Error rate: Target < 0.1%
- Uptime: Target > 99.9%
- Database query time: Target < 100ms

---

## Rollback Procedure

```bash
# If deployment fails:
heroku rollback                 # Heroku
git revert HEAD                 # Git
eb abort                        # Elastic Beanstalk
kubectl rollout undo deployment # Kubernetes
```
