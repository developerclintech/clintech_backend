from __future__ import annotations

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.monitoring import MetricsMiddleware, metrics_response
from app.middleware.request_context import RequestContextMiddleware


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

    return application


app = create_app()
