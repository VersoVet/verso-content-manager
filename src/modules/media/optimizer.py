"""Image optimization for WordPress media library."""

import io
import logging

import httpx
from PIL import Image

from src.config import (
    IMAGE_COLUMN_MAX_HEIGHT,
    IMAGE_COLUMN_MAX_WIDTH,
    IMAGE_MAX_HEIGHT,
    IMAGE_MAX_WIDTH,
    WEBP_QUALITY,
)

logger = logging.getLogger(__name__)


async def download_image(url: str) -> bytes:
    """Download image from URL.

    Args:
        url: Image URL to download.

    Returns:
        Image bytes.

    Raises:
        ValueError: If download fails.
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.content
    except Exception as e:
        logger.error(f"Failed to download image from {url}: {str(e)}")
        raise ValueError(f"Failed to download image: {str(e)}")


def optimize_image(image_bytes: bytes, context: str = "article", filename: str = "image") -> tuple[bytes, str]:
    """Optimize image and convert to WebP.

    Args:
        image_bytes: Raw image bytes.
        context: Context for sizing (featured, article, column).
        filename: Original filename for extension detection.

    Returns:
        Tuple of (webp_bytes, filename.webp).

    Raises:
        ValueError: If image processing fails.
    """
    try:
        # Open image from bytes
        img = Image.open(io.BytesIO(image_bytes))

        # Convert RGBA to RGB if needed
        if img.mode in ("RGBA", "LA", "P"):
            rgb_img = Image.new("RGB", img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
            img = rgb_img  # type: ignore[assignment]

        # Resize based on context
        if context == "featured":
            img.thumbnail((IMAGE_MAX_WIDTH, IMAGE_MAX_HEIGHT), Image.Resampling.LANCZOS)
        elif context == "column":
            img.thumbnail(
                (IMAGE_COLUMN_MAX_WIDTH, IMAGE_COLUMN_MAX_HEIGHT),
                Image.Resampling.LANCZOS,
            )
        else:  # article
            img.thumbnail((IMAGE_MAX_WIDTH, IMAGE_MAX_HEIGHT), Image.Resampling.LANCZOS)

        # Convert to WebP
        webp_buffer = io.BytesIO()
        img.save(webp_buffer, format="WEBP", quality=WEBP_QUALITY, method=6)
        webp_bytes = webp_buffer.getvalue()

        # Generate filename
        webp_filename = f"{filename.split('.')[0]}.webp"

        logger.info(f"Optimized {filename} ({len(image_bytes)} → {len(webp_bytes)} bytes)")
        return webp_bytes, webp_filename

    except Exception as e:
        logger.error(f"Failed to optimize image: {str(e)}")
        raise ValueError(f"Failed to optimize image: {str(e)}")


async def optimize_and_prepare(url: str, context: str = "article", filename: str = "image") -> tuple[bytes, str]:
    """Download and optimize image in one operation.

    Args:
        url: Image URL.
        context: Context for sizing.
        filename: Original filename.

    Returns:
        Tuple of (webp_bytes, webp_filename).
    """
    image_bytes = await download_image(url)
    return optimize_image(image_bytes, context, filename)
