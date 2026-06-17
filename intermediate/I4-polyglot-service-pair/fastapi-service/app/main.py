from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routes.convert import router as convert_router

app = FastAPI(
    title="Currency Converter API",
    description="Hardcoded currency conversion service for I4 polyglot pair",
    version="1.0.0",
)

app.include_router(convert_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
