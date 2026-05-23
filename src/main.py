"""FastAPI application for verso-content-manager."""

import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from src.config import PORT, SERVICE_NAME
from src.dashboard import DASHBOARD_HTML
from src.modules.articles.routes import router as articles_router
from src.modules.content.routes import router as content_router
from src.modules.media.routes import router as media_router
from src.modules.seo.routes import router as seo_router
from src.modules.templates.routes import router as templates_router

try:
    from onyx_sdk import OnyxClient, SkillStatus  # type: ignore[import-untyped]
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False
    SkillStatus = None  # type: ignore[assignment]


class _NullOnyx:
    """Stub client when SDK is unavailable."""

    def status(self, *args: Any, **kwargs: Any) -> None:
        """No-op status report."""


logger = logging.getLogger(__name__)
_onyx_client: Any = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    """Manage application lifespan.

    Args:
        app: FastAPI application instance.

    Yields:
        Control to application.
    """
    global _onyx_client

    logger.info(f"{SERVICE_NAME} started on port {PORT}")

    # Initialize Onyx SDK if available
    if SDK_AVAILABLE:
        try:
            _onyx_client = OnyxClient(SERVICE_NAME, "cerebellum", port=PORT)
            _onyx_client.status(SkillStatus.STARTING, "Initializing...")
            _onyx_client.status(SkillStatus.UP, "Ready")
            logger.info("Onyx SDK initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Onyx SDK: {e}")
            _onyx_client = _NullOnyx()
    else:
        _onyx_client = _NullOnyx()

    yield

    # Shutdown
    if _onyx_client and isinstance(_onyx_client, OnyxClient):
        _onyx_client.status(SkillStatus.DOWN, "Shutting down")

    logger.info(f"{SERVICE_NAME} shutting down")


app = FastAPI(
    title="verso-content-manager",
    description="WordPress article management with JSON blocks",
    version="1.0.0",
    lifespan=lifespan,
)

# Include routers
app.include_router(articles_router)
app.include_router(content_router)
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
