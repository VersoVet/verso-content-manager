"""FastAPI routes for media management."""

import logging

from fastapi import APIRouter, HTTPException

from src.models import MediaResponse, MediaUploadRequest
from src.modules.media.uploader import upload_from_url

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/media", tags=["media"])


@router.post("/upload", response_model=MediaResponse)
async def upload_media_endpoint(request: MediaUploadRequest) -> MediaResponse:
    """Upload media from URL to WordPress library.

    Args:
        request: MediaUploadRequest with URL and optional alt text.

    Returns:
        MediaResponse with uploaded media details.
    """
    try:
        # Extract filename from URL
        filename = request.url.split("/")[-1].split("?")[0] or "image.webp"

        media = await upload_from_url(
            url=request.url,
            alt_text=request.alt,
            title=request.title,
            filename=filename,
        )

        logger.info(f"Uploaded media: {media.id} ({filename})")
        return media
    except Exception as e:
        logger.error(f"Failed to upload media: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
