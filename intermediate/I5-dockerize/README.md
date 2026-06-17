# I5 — Dockerize Currency Converter Service

Containerizes the **I4 FastAPI Currency Converter** (`intermediate/I4-fastapi-node-pair/fastapi-service/`).

## Overview

| Item | Value |
|------|-------|
| Service | I4 Currency Converter API |
| Image name | `eval-service` |
| Container port | `8000` |
| Base image | `python:3.11-slim` |

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed and running
- Source service at `../I4-fastapi-node-pair/fastapi-service/`

## Build

Build context is the FastAPI service directory; Dockerfile lives in this folder.

```bash
cd ../I4-fastapi-node-pair/fastapi-service
docker build -f ../../I5-dockerize/Dockerfile -t eval-service .
```

## Run

```bash
docker run -d -p 8000:8000 --name eval-service eval-service
```

## Verify

```bash
curl http://localhost:8000/health
curl http://localhost:8000/docs
curl -X POST http://localhost:8000/convert \
  -H "Content-Type: application/json" \
  -d '{"amount":100,"from_currency":"USD","to_currency":"INR"}'
```

Expected health response:

```json
{"status":"UP"}
```

## Stop

```bash
docker stop eval-service
docker rm eval-service
```

## Files

| File | Purpose |
|------|---------|
| `Dockerfile` | Multi-stage-ready production image definition |
| `.dockerignore` | Excludes tests, venv, cache from image context |
| `docs/DOCKER_REPORT.md` | Build/run verification report |

## Image details

- Non-root `app` user
- `HEALTHCHECK` on `/health`
- `uvicorn` bound to `0.0.0.0:8000`
