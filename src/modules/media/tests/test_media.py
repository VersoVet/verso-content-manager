"""Tests for media module."""

from typing import Any

import pytest


@pytest.mark.asyncio
async def test_create_media_from_url_invalid_url(mocker: Any) -> None:
    """Test media creation with invalid URL.

    Args:
        mocker: Pytest mocker fixture.
    """
    from src.modules.media.service import create_media_from_url

    # Mock download to fail
    mocker.patch("src.modules.media.service.download_image", side_effect=ValueError("Invalid URL"))

    with pytest.raises(ValueError, match="Failed to create media"):
        await create_media_from_url("http://invalid.url/image.jpg")


@pytest.mark.asyncio
async def test_create_media_success(mocker: Any) -> None:
    """Test successful media creation.

    Args:
        mocker: Pytest mocker fixture.
    """
    from src.models import MediaResponse
    from src.modules.media.service import create_media_from_url

    # Mock the pipeline
    mocker.patch("src.modules.media.service.download_image", return_value=b"fake_image_data")
    mocker.patch("src.modules.media.service.optimize_image", return_value=(b"fake_webp", "image.webp"))
    mocker.patch(
        "src.modules.media.service.upload_media",
        return_value=MediaResponse(
            id=123, wp_url="https://verso-vet.com/wp-content/uploads/image.webp", filename="image.webp", size=100
        ),
    )

    result = await create_media_from_url("http://example.com/image.jpg", alt_text="Test image")

    assert result.id == 123
    assert "image.webp" in result.wp_url
