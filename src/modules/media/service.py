"""Media management service orchestrating upload and optimization."""

import logging

from src.models import MediaResponse
from src.modules.media.optimizer import download_image, optimize_image
from src.modules.media.uploader import upload_media

logger = logging.getLogger(__name__)


async def create_media_from_url(
    url: str, alt_text: str = "", title: str | None = None, context: str = "article"
) -> MediaResponse:
    """Create and upload media from external URL with optimization.

    Orchestrates the full pipeline: download → optimize → upload.

    Args:
        url: External image URL.
        alt_text: Alt text description.
        title: Media title.
        context: Sizing context (featured, article, column).

    Returns:
        MediaResponse with WordPress media details.

    Raises:
        ValueError: If any step fails.
    """
    try:
        # Download image
        image_bytes = await download_image(url)

        # Optimize image
        optimized_bytes, filename = optimize_image(image_bytes, context=context)

        # Upload to WordPress
        response = await upload_media(filename, optimized_bytes, alt_text, title)

        logger.info(f"Media created from {url}: {response.wp_url}")
        return response

    except Exception as e:
        logger.error(f"Failed to create media from {url}: {str(e)}")
        raise ValueError(f"Failed to create media: {str(e)}")
