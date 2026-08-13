# FocusDNA AI — Multi-Stage Production Dockerfile for FastAPI Backend

# Stage 1: Build & Dependencies
FROM python:3.9-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY apps/api/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt \
    && pip install --no-cache-dir --prefix=/install gunicorn uvicorn joblib pandas scikit-learn numpy

# Stage 2: Final Production Runner
FROM python:3.9-slim AS runner

WORKDIR /app

# Create non-root system user for security
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local
COPY apps/api /app
COPY ml /app/ml

# Set Python Path & Production Environment
ENV PYTHONPATH=/app:/app/ml
ENV PORT=8000
ENV ENVIRONMENT=production

# Grant permissions to appuser
RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

# Container Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl --fail http://localhost:8000/health || exit 1

# Production Gunicorn Multi-Worker Server Command
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8000"]
