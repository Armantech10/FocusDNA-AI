# FocusDNA AI — Production Deployment Guide

This guide details the complete production deployment procedure for FocusDNA AI across Supabase, Vercel, Dockerized FastAPI backend, ML artifacts, custom domains, and Chrome extension manifest configurations.

---

## 1. Supabase Production Project Setup

1. **Create Supabase Project**:
   - Log in to [Supabase Console](https://supabase.com/dashboard) and create a production project named `FocusDNA Production`.
   - Copy `Project URL` (`https://<project-ref>.supabase.co`) and `anon` / `service_role` keys.

2. **Execute Database Migrations**:
   - Navigate to the Supabase SQL Editor and execute the schema initialization SQL:
     ```sql
     -- 1. Focus Sessions Table
     CREATE TABLE IF NOT EXISTS public.focus_sessions (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       user_id TEXT NOT NULL,
       session_name TEXT NOT NULL,
       planned_duration_minutes INT NOT NULL,
       actual_duration_minutes INT DEFAULT 0,
       status TEXT NOT NULL DEFAULT 'active',
       distraction_count INT DEFAULT 0,
       app_switch_count INT DEFAULT 0,
       started_at TIMESTAMPTZ DEFAULT NOW(),
       completed_at TIMESTAMPTZ
     );

     -- 2. Activity Events Telemetry Table
     CREATE TABLE IF NOT EXISTS public.activity_events (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       user_id TEXT NOT NULL,
       application_name TEXT,
       website_domain TEXT,
       category TEXT,
       session_duration INT DEFAULT 0,
       app_switch_count INT DEFAULT 0,
       browser_switch_count INT DEFAULT 0,
       idle_seconds INT DEFAULT 0,
       timestamp TIMESTAMPTZ DEFAULT NOW()
     );

     -- Enable Row Level Security (RLS)
     ALTER TABLE public.focus_sessions ENABLE ROW LEVEL SECURITY;
     ALTER TABLE public.activity_events ENABLE ROW LEVEL SECURITY;

     -- Enable User Isolation RLS Policies
     CREATE POLICY "Users access own focus_sessions" ON public.focus_sessions
       FOR ALL USING (auth.uid()::text = user_id);

     CREATE POLICY "Users access own activity_events" ON public.activity_events
       FOR ALL USING (auth.uid()::text = user_id);
     ```

---

## 2. Environment Variables Configuration

Copy `.env.example` to your environment settings and populate production variables:

### Frontend (Vercel):
- `NEXT_PUBLIC_SUPABASE_URL`: `https://<project-ref>.supabase.co`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`: `eyJhbGciOi...`
- `NEXT_PUBLIC_API_URL`: `https://api.focusdna.ai`

### Backend (Docker Container / AWS / Render / Railway):
- `ENVIRONMENT`: `production`
- `CORS_ORIGINS`: `https://focusdna.ai,https://app.focusdna.ai`
- `SUPABASE_URL`: `https://<project-ref>.supabase.co`
- `SUPABASE_SERVICE_ROLE_KEY`: `eyJhbGciOi...`
- `GEMINI_API_KEY`: `AIzaSyB...`
- `DATABASE_URL`: `postgresql://postgres:<password>@db.<project-ref>.supabase.co:6543/postgres`

---

## 3. Vercel Next.js Frontend Deployment

1. Connect your GitHub repository to Vercel.
2. Set Root Directory to `apps/web`.
3. Framework Preset: `Next.js`.
4. Build Command: `npm run build`.
5. Add Frontend Environment Variables (`NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `NEXT_PUBLIC_API_URL`).
6. Click **Deploy**. Vercel will build all 20 static and dynamic routes.

---

## 4. Containerized FastAPI Backend Deployment (Docker)

1. **Build Container Image**:
   ```bash
   docker build -t focusdna-api:latest -f Dockerfile .
   ```

2. **Test Locally with Docker Compose**:
   ```bash
   docker-compose up --build -d
   ```
   Verify health check at `http://localhost:8000/health`.

3. **Deploy Container to Backend Host (Render / Railway / AWS ECS)**:
   - Push container image to Docker Hub or AWS ECR:
     ```bash
     docker tag focusdna-api:latest registry.hub.docker.com/your-org/focusdna-api:v1.0.0
     docker push registry.hub.docker.com/your-org/focusdna-api:v1.0.0
     ```
   - Configure health check path: `/health` (Interval: 30s).
   - Set start command: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000`.

---

## 5. Database Migrations

Use Supabase CLI or SQL Editor to apply migrations idempotently:
```bash
supabase db push --linked
```
Verify index creation on `user_id` and `timestamp` fields for sub-10ms telemetry aggregation queries.

---

## 6. ML Model Deployment & Artifact Packaging

1. Serialized machine learning models (`ml/models/attention_loss_model.joblib` and `ml/models/anomaly_model.joblib`) are pre-built and packaged inside the Docker container image.
2. The FastAPI `PredictiveAttentionService` loads joblib artifacts into memory at startup as a singleton service (**zero per-request disk reads or retraining overhead**).
3. If new models pass the evaluation gates in `ml/pipeline/retrain_pipeline.py`, rebuild and push the Docker image to update production models cleanly.

---

## 7. Domain Configuration & HTTPS / SSL

1. **DNS A & CNAME Records**:
   - `app.focusdna.ai` -> Points to Vercel CNAME (`cname.vercel-dns.com`).
   - `api.focusdna.ai` -> Points to Backend Load Balancer / Host IP.
2. **CORS Configuration**:
   Ensure `CORS_ORIGINS` includes `https://app.focusdna.ai`.
3. **HTTPS / SSL**:
   All HTTP traffic is automatically redirected to HTTPS via Vercel Edge Network and Let's Encrypt / AWS ACM TLS certificates.

---

## 8. Chrome Extension Production Configuration

Before publishing or loading the Chrome Manifest V3 Extension in Chrome:
1. Update `apps/extension/manifest.json`:
   ```json
   "host_permissions": [
     "https://api.focusdna.ai/*"
   ]
   ```
2. Update `apps/extension/api.js`:
   ```javascript
   const API_BASE = "https://api.focusdna.ai";
   ```
3. Load unpacked extension in Chrome -> `chrome://extensions` -> Load Unpacked -> Select `apps/extension/`.

---

## 9. Verification & End-to-End Test

Execute the full platform health audit:
1. `curl https://api.focusdna.ai/health` -> Returns `{"status":"ok"}`.
2. Open `https://app.focusdna.ai/dashboard` -> Verify metric rendering.
3. Start a focus session -> Verify session state synchronizes across frontend and FastAPI backend.
