from __future__ import annotations

import os

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.middleware.observability import ObservabilityMiddleware, configure_logging
from app.routes.transactions import router as transactions_router

configure_logging()

app = FastAPI(
    title="Transaction Service",
    description="In-memory transaction management API with observability",
    version="1.1.0",
)

app.add_middleware(ObservabilityMiddleware)
app.include_router(transactions_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


@app.get("/", tags=["root"])
def root() -> dict[str, object]:
    return {
        "service": "b4-transaction-api",
        "message": "D6 observability API — dashboards are in Grafana, not here",
        "endpoints": {
            "health": "/health",
            "metrics": "/metrics",
            "docs": "/docs",
            "transactions": "/transactions",
            "balance": "/balance",
        },
        "grafana": "http://localhost:3002 (admin/admin) — dashboard: API Observability",
        "prometheus": "http://localhost:9090",
    }


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    if os.getenv("ENVIRONMENT"):
        return {"status": "UP"}
    return {"status": "ok"}


@app.get("/metrics", tags=["observability"])
def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
