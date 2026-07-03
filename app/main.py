from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, OperationalError

from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.monitoring import MetricsMiddleware, metrics_response
from app.middleware.request_context import RequestContextMiddleware

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings)

    application = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    application.add_middleware(RequestContextMiddleware)

    if settings.ENABLE_METRICS:
        application.add_middleware(MetricsMiddleware)
        application.add_api_route("/metrics", metrics_response, include_in_schema=False)

    application.include_router(api_router, prefix=settings.API_V1_PREFIX)

    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors()},
        )

    @application.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
        logger.warning("Database integrity error on %s %s", request.method, request.url.path, exc_info=exc)
        return JSONResponse(
            status_code=409,
            content={"detail": "A record with the provided data already exists."},
        )

    @application.exception_handler(OperationalError)
    async def operational_error_handler(request: Request, exc: OperationalError) -> JSONResponse:
        logger.error("Database operational error on %s %s", request.method, request.url.path, exc_info=exc)
        return JSONResponse(
            status_code=503,
            content={"detail": "Service temporarily unavailable. Please try again later."},
        )

    @application.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected error occurred. Please try again later."},
        )

    return application


app = create_app()
