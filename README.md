# FocusDNA AI — Predictive Attention Intelligence

FocusDNA AI is a privacy-first digital-wellness platform that learns user behavioral patterns and predicts attention loss without capturing raw text or keystrokes.

---

## Monorepo Layout

```
focusdna/
├── apps/
│   ├── web/           # Next.js Frontend (TypeScript, Supabase Auth, Middleware Route Protection)
│   ├── api/           # FastAPI Backend (JWT Bearer Security Guard, Profile & Events Endpoints)
│   ├── extension/     # Chrome Extension Manifest V3 Placeholder
│   └── desktop/       # Electron Desktop Agent Placeholder
├── ml/                # ML Pipeline Modules Placeholder (Phase 4)
├── docs/              # Architectural Documentation (ARCHITECTURE.md)
├── infrastructure/    # Supabase Schemas & Docker Compose
│   └── supabase/
│       └── migrations/
│           ├── 001_initial_schema.sql
│           └── 002_phase2_schema.sql   # PostgreSQL 10 tables & Row Level Security (RLS) policies
├── .env.example
└── README.md
```

---

## Phase 2: Authentication & Database Configuration

### 1. Supabase PostgreSQL Schema & RLS Setup
- Run `infrastructure/supabase/migrations/002_phase2_schema.sql` in your Supabase SQL Editor.
- Enforces **Row Level Security (RLS)** across all 10 user tables (`profiles`, `privacy_settings`, `focus_sessions`, `activity_events`, `distraction_events`, `focus_scores`, `ml_features`, `ml_predictions`, `user_feedback`, `ai_recommendations`). Every record is strictly isolated to `auth.uid() = user_id`.

### 2. Frontend Auth & Protected Routes (`apps/web`)
- **Authentication**: Sign up (`/signup`), Login (`/login`), Password Reset (`/reset-password`, `/update-password`), Logout (Navbar dropdown).
- **Route Protection**: `middleware.ts` intercepts `/dashboard`, `/onboarding`, `/settings`, `/focus` and redirects unauthenticated users to `/login`.
- **Onboarding Page (`/onboarding`)**: Captures Display Name, Timezone, Tracking Consent toggle, and zero-keystroke privacy explanation.
- **Privacy Settings Page (`/settings`)**: Provides tracking pause toggle and permanent data purge trigger.

### 3. Backend JWT Authentication Guard (`apps/api`)
- FastAPI security dependency `get_current_user` decodes & verifies Supabase JWT access tokens from `Authorization: Bearer <token>`.
- Rejects unauthenticated requests with `HTTP 401 Unauthorized`.
- Guarantees backend user isolation across profile and activity endpoints.

---

## How to Start Locally

### 1. Start FastAPI Backend (`apps/api`)
```bash
cd apps/api
python3 -m pip install -r requirements.txt
python3 -m uvicorn main:app --reload --port 8000
```
- Health Check: `http://localhost:8000/health` (Returns `{"status": "ok"}`)
- API Documentation: `http://localhost:8000/docs`

### 2. Run Backend Unit & Auth Test Suite
```bash
PYTHONPATH=apps/api python3 -m pytest apps/api/tests
```

### 3. Start Next.js Web Frontend (`apps/web`)
```bash
cd apps/web
npm install
npm run dev
```
- Web Application: `http://localhost:3000`
- Sign Up: `http://localhost:3000/signup`
- Login: `http://localhost:3000/login`
- Dashboard Shell (Protected): `http://localhost:3000/dashboard`
- Onboarding (Protected): `http://localhost:3000/onboarding`
- Privacy Settings (Protected): `http://localhost:3000/settings`
