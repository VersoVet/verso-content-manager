"""WordPress media library uploader."""

import logging

from src.core.wp_client import wp_post
from src.models import MediaResponse

logger = logging.getLogger(__name__)


async def upload_media(
    filename: str, content: bytes, alt_text: str = "", title: str | None = None
) -> MediaResponse:
    """Upload media to WordPress library.

    Args:
        filename: Filename for the media (e.g., image.webp).
        content: Binary content of the file.
        alt_text: Alt text for the media.
        title: Title for the media.

    Returns:
        MediaResponse with upload details.

    Raises:
        ValueError: If upload fails.
    """
    try:
        # Upload to WordPress media library
        resp = await wp_post(
            "/wp/v2/media",
            data={
                "file": (filename, content, "image/webp"),
            },
        )

        # Update alt text and title if provided
        if alt_text or title:
            update_data = {}
            if alt_text:
                update_data["alt_text"] = alt_text
            if title:
                update_data["title"] = title

            if update_data:
                resp = await wp_post(f"/wp/v2/media/{resp['id']}", json_data=update_data)

        return MediaResponse(
            id=resp["id"],
            wp_url=resp.get("source_url", resp.get("guid", {}).get("rendered", "")),
            filename=filename,
            size=len(content),
        )

    except Exception as e:
        logger.error(f"Failed to upload media {filename}: {str(e)}")
        raise ValueError(f"Failed to upload media: {str(e)}")


async def upload_from_url(
    url: str, alt_text: str = "", title: str | None = None, filename: str = "image.webp"
) -> MediaResponse:
    """Upload media from external URL (convenience wrapper).

    Args:
        url: Image URL.
        alt_text: Alt text.
        title: Title.
        filename: Filename to use in WordPress.

    Returns:
        MediaResponse with upload details.
    """
    # Import here to avoid circular dependency
    from src.modules.media.optimizer import optimize_and_prepare

    webp_bytes, webp_filename = await optimize_and_prepare(url, context="article", filename=filename)
    return await upload_media(webp_filename, webp_bytes, alt_text, title)
