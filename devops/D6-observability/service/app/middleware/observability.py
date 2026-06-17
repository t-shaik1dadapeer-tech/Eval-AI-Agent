from __future__ import annotations

import json
import logging
import time
import uuid
from datetime import UTC, datetime

from prometheus_client import Counter, Histogram
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)
HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)
REQUEST_COUNT_BY_ENDPOINT = Counter(
    "request_count_by_endpoint",
    "Request count grouped by endpoint path",
    ["endpoint"],
)
ERROR_COUNT = Counter(
    "error_count",
    "HTTP responses with status >= 400",
    ["method", "path", "status"],
)

access_logger = logging.getLogger("access")


class ObservabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        start = time.perf_counter()
        status_code = 500
        response: Response | None = None

        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            duration_seconds = time.perf_counter() - start
            latency_ms = round(duration_seconds * 1000, 2)
            method = request.method
            path = request.url.path
            status = str(status_code)

            HTTP_REQUESTS_TOTAL.labels(method=method, path=path, status=status).inc()
            HTTP_REQUEST_DURATION_SECONDS.labels(method=method, path=path).observe(
                duration_seconds
            )
            REQUEST_COUNT_BY_ENDPOINT.labels(endpoint=path).inc()
            if status_code >= 400:
                ERROR_COUNT.labels(method=method, path=path, status=status).inc()

            log_entry = {
                "timestamp": datetime.now(UTC).isoformat(),
                "method": method,
                "path": path,
                "status": status_code,
                "latency_ms": latency_ms,
                "request_id": request_id,
            }
            access_logger.info(json.dumps(log_entry, separators=(",", ":")))

            if response is not None:
                response.headers["X-Request-ID"] = request_id


def configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    access_logger.handlers.clear()
    access_logger.addHandler(handler)
    access_logger.setLevel(logging.INFO)
    access_logger.propagate = False
