"""FastAPI routes for content publishing."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from src.models import PublishRequest, PublishResponse
from src.modules.content.service import publish_written_content

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/content", tags=["content"])


def _get_onyx_client() -> Any:
    """Get global Onyx client from main module.

    Returns:
        OnyxClient instance or _NullOnyx stub.
    """
    try:
        from src.main import _onyx_client  # type: ignore[import]

        return _onyx_client
    except ImportError:
        return None


@router.post("/publish", response_model=PublishResponse)
async def publish_content_endpoint(request: PublishRequest) -> PublishResponse:
    """Publish WrittenContent from article-writer to WordPress.

    Accepts output from article-writer skill (WrittenContent JSON),
    downloads and optimizes images, converts markdown to HTML,
    and publishes article to verso-vet.com.

    Args:
        request: PublishRequest with WrittenContent.

    Returns:
        PublishResponse with post ID, URL, and status.
    """
    onyx = _get_onyx_client()
    if onyx:
        try:
            from onyx_sdk import SkillStatus  # type: ignore[import-untyped]

            onyx.status(SkillStatus.WORKING, "Publishing article...")
        except ImportError:
            pass

    try:
        return await publish_written_content(request)
    except Exception as e:
        logger.error(f"Failed to publish content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
