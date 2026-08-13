# FocusDNA AI — System Architecture

```
focusdna/
├── apps/
│   ├── web/           # Next.js Frontend (TypeScript, Tailwind CSS, Navigation & Dashboard Shell)
│   ├── api/           # FastAPI Backend (CORS, Health Endpoint GET /health)
│   ├── extension/     # Chrome Extension (Manifest V3 Scaffolding)
│   └── desktop/       # Electron Desktop Agent (Scaffolding)
├── ml/                # ML Pipeline Modules (Phase 4)
├── docs/              # Architectural Documentation
├── infrastructure/    # Docker Compose & Cloud Deployments
├── .env.example
└── README.md
```

## System Communication Flow

```
[ Next.js Web App ]  ---> (HTTP CORS GET /health) ---> [ FastAPI Backend ]
[ Chrome Extension ] ---> (Telemetry API Ingestion) -> [ FastAPI Backend ]
[ Desktop Agent ]    ---> (Telemetry API Ingestion) -> [ FastAPI Backend ]
```
