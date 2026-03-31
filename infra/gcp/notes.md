# GCP Deployment Notes

## Option A: Cloud Run (Recommended for small scale)

### Backend
- Build Docker image and push to Google Artifact Registry
- Deploy to Cloud Run with env vars from Secret Manager
- Set min instances = 1 to avoid cold starts

```bash
gcloud run deploy wealthos-backend \
  --image gcr.io/YOUR_PROJECT/wealthos-backend \
  --platform managed \
  --region me-central1 \
  --set-env-vars DATABASE_URL=... \
  --allow-unauthenticated
```

### Frontend
- Build Next.js standalone output (already configured in next.config.js)
- Deploy to Cloud Run or Firebase Hosting

### Database
- Use Cloud SQL (PostgreSQL 15)
- Enable Cloud SQL Auth Proxy for secure connections

## Option B: Compute Engine VM

1. Create an e2-medium VM (or larger for production)
2. Install Docker and docker-compose
3. Clone repo, set .env, run: `docker compose up -d`
4. Use Cloud Load Balancing + SSL certificate

## Managed Database
```bash
gcloud sql instances create wealthos-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=me-central1
```

## Secrets
Use Secret Manager for all sensitive values:
```bash
echo -n "your-secret-key" | gcloud secrets create wealthos-secret-key --data-file=-
```
