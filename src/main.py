"""FastAPI application for verso-content-manager."""

import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from src.config import PORT, SERVICE_NAME
from src.dashboard import DASHBOARD_HTML
from src.modules.articles.routes import router as articles_router
from src.modules.media.routes import router as media_router
from src.modules.seo.routes import router as seo_router
from src.modules.templates.routes import router as templates_router

try:
    from onyx_sdk import OnyxClient  # type: ignore[import-untyped]
    _onyx_client = OnyxClient()
except ImportError:
    _onyx_client = None

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    """Manage application lifespan.

    Args:
        app: FastAPI application instance.

    Yields:
        Control to application.
    """
    logger.info(f"{SERVICE_NAME} started on port {PORT}")
    if _onyx_client:
        await _onyx_client.start()
    yield
    if _onyx_client:
        await _onyx_client.stop()
    logger.info(f"{SERVICE_NAME} shutting down")


app = FastAPI(
    title="verso-content-manager",
    description="WordPress article management with JSON blocks",
    version="1.0.0",
    lifespan=lifespan,
)

# Include routers
app.include_router(articles_router)
app.include_router(media_router)
app.include_router(seo_router)
app.include_router(templates_router)


@app.get("/", response_class=HTMLResponse)
async def dashboard() -> str:
    """Serve interactive dashboard.

    Returns:
        HTML dashboard.
    """
    return DASHBOARD_HTML


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        Health status.
    """
    return {
        "status": "healthy",
        "service": SERVICE_NAME,
        "version": "1.0.0",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=PORT,
        reload=False,
    )
