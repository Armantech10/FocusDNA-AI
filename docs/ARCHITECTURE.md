# FocusDNA AI — System Architecture Specification

This document details the system architecture, component interactions, data flow, machine learning pipeline, and security boundaries of FocusDNA AI.

---

## 1. High-Level Architecture Diagram

```mermaid
graph TD
    %% User Clients
    subgraph Clients["User Client Layer"]
        Web["Next.js 14 Web Application<br/>(React 18 + Recharts)"]
        Ext["Chrome Manifest V3 Extension<br/>(Domain Telemetry)"]
        Desk["macOS Electron Desktop Agent<br/>(Process Poller + Offline Queue)"]
    end

    %% API Backend Service
    subgraph Backend["FastAPI Backend Services (Python 3.9)"]
        Router["FastAPI Router & Authentication"]
        Heuristic["Heuristic Feature Engine"]
        ML_Service["Predictive ML Inference Engine"]
        Profile_Svc["FocusDNA Profile Aggregator"]
        Gemini_Svc["Gemini AI Recommendation Service"]
    end

    %% External Infrastructure & Persistence
    subgraph Infrastructure["Persistence & External Services"]
        Supabase[("Supabase PostgreSQL DB<br/>Row-Level Security Enabled")]
        Gemini_API["Google Gemini 1.5 Flash API"]
    end

    %% Data Flow Connections
    Web -->|JWT Bearer Auth / REST| Router
    Ext -->|POST /api/events| Router
    Desk -->|POST /api/events / Offline Sync| Router

    Router -->|Read / Write Telemetry| Supabase
    Router -->|Compute Scored Features| Heuristic
    Router -->|Evaluate Model Probabilities| ML_Service
    Router -->|Aggregate Behavioral Metrics| Profile_Svc
    Router -->|Generate Interventions| Gemini_Svc

    Gemini_Svc -->|Structured Statistics JSON| Gemini_API
    Gemini_API -->|Actionable Interventions| Gemini_Svc

    ML_Service -->|Attention Loss Prob & Anomaly Signal| Router
    Profile_Svc -->|Typical Session & Peak Hours| Router
    Heuristic -->|Rule-Based Score (0-100)| Router

    Router -->|Real-Time Insights & ML Cards| Web
```

---

## 2. Sub-System Component Breakdown

### A. Web Application (`apps/web/`)
- **Framework**: Next.js 14 (App Router), React 18, TypeScript, TailwindCSS.
- **Data Visualization**: Recharts (`FocusTimeChart`, `DistractionChart`, `AppSwitchingChart`).
- **State Management**: Local state with Supabase Auth client & `localStorage` fallback.
- **Pages (20 Routes)**: `/dashboard`, `/focus`, `/analytics`, `/focusdna`, `/recommendations`, `/history`, `/privacy`, `/settings`, `/status`, `/login`, `/signup`, `/onboarding`, `/reset-password`, `/update-password`.

### B. FastAPI Backend Service (`apps/api/`)
- **Framework**: FastAPI (Python 3.9), Pydantic v2 validation models.
- **Process Manager**: Gunicorn with Uvicorn worker threads (`uvicorn.workers.UvicornWorker`).
- **Routers**:
  - `sessions.py`: Focus session engine & pomodoro state manager (`POST /api/sessions`).
  - `events.py`: Behavioral telemetry event ingestion (`POST /api/events`).
  - `predictions.py`: ML model inference endpoint (`POST /api/ml/predict`).
  - `recommendations.py`: Google Gemini AI recommendation engine (`POST /api/ai/recommendation`).
  - `feedback.py`: User feedback loop & offline retraining trigger (`POST /api/feedback`).
  - `profile.py`: FocusDNA profile aggregator & Privacy Data Rights endpoints (`GET /api/privacy/export`, `POST /api/privacy/purge`).

### C. Machine Learning Engine (`ml/`)
- **Supervised Classifier**: Gradient Boosted Trees (`F1-Score: 0.9776`) trained on behavioral feature vectors.
- **Unsupervised Anomaly Detector**: `IsolationForest` model identifying 90m entertainment activity spikes.
- **Retraining Pipeline**: Controlled offline retraining script [ml/pipeline/retrain_pipeline.py](ml/pipeline/retrain_pipeline.py) gated by holdout F1-Score evaluation comparisons.

### D. Chrome Extension (`apps/extension/`)
- **Manifest Version**: Manifest V3 background service worker.
- **Permissions**: `tabs`, `idle`, `storage`, `alarms`, `activeTab`.
- **Privacy Boundary**: Tracks domain names (`github.com`) and tab switch frequency only. Zero text or keystroke collection.

### E. macOS Electron Desktop Agent (`apps/desktop/`)
- **Stack**: Electron 28, Node.js, IPC ContextBridge preload script.
- **Native Poller**: Queries macOS active process name via AppleScript (`osascript`) and system idle seconds via `ioreg`.
- **Offline Event Queue**: Persists telemetry locally in `apps/desktop/data/offline_queue.json` when backend connectivity is offline, automatically retrying sync upon reconnection.

---

## 3. Data Flow & Security Boundaries

```
[User Browser/Desktop Activity]
              │
              ▼
   (Metadata Extraction: App Name & Domain ONLY)
              │
              ▼
   (In-Memory & Offline Queue Storage)
              │
              ▼
   [HTTPS POST /api/events with JWT Auth Header]
              │
              ▼
   [FastAPI Input Validation via Pydantic]
              │
              ▼
   [Supabase PostgreSQL Persistence (RLS Protected)]
```
