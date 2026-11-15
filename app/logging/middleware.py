import time
import uuid
from collections.abc import Callable
from contextvars import ContextVar

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(  # type: ignore[override]
        self, request: Request, call_next: Callable[[Request], Response]
    ) -> Response:
        request_id = str(uuid.uuid4())
        token = request_id_var.set(request_id)
        response = None

        start = time.perf_counter()
        logger.bind(channel="api").info(f"Request start {request.method} {request.url.path}")
        try:
            response = await call_next(request)
        except Exception:
            logger.exception("Unhandled error while processing request")
            raise
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.bind(channel="api").info(
                f"Request end {request.method} {request.url.path} "
                f"status={getattr(response, 'status_code', 'unknown')} "
                f"latency_ms={elapsed_ms:.2f}"
            )
            request_id_var.reset(token)

        response.headers["X-Request-ID"] = request_id
        return response
