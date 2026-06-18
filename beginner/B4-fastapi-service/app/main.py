from __future__ import annotations

import os

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routes.transactions import router as transactions_router

app = FastAPI(
    title="Transaction Service",
    description="In-memory transaction management and balance calculation API",
    version="1.0.0",
)

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
        "endpoints": ["/health", "/docs", "/transactions", "/balance"],
    }


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    if os.getenv("ENVIRONMENT"):
        return {"status": "UP"}
    return {"status": "ok"}
