from __future__ import annotations

from fastapi import FastAPI

from app.database import wait_for_database
from app.routes import router as transactions_router

app = FastAPI(title="D2 Transaction API", version="1.0.0")


@app.on_event("startup")
def startup() -> None:
    wait_for_database()


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "UP"}


app.include_router(transactions_router)
