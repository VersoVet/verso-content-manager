"""Tests for SEO module."""

from typing import Any

import pytest


@pytest.mark.asyncio
async def test_get_categories_success(mocker: Any) -> None:
    """Test retrieving categories successfully.

    Args:
        mocker: Pytest mocker fixture.
    """
    from src.modules.seo.service import get_categories

    mock_response = [{"id": 1, "name": "Santé", "slug": "sante"}]
    mocker.patch("src.modules.seo.service.wp_get", return_value=mock_response)

    result = await get_categories()
    assert len(result) == 1
    assert result[0]["name"] == "Santé"


@pytest.mark.asyncio
async def test_get_tags_success(mocker: Any) -> None:
    """Test retrieving tags successfully.

    Args:
        mocker: Pytest mocker fixture.
    """
    from src.modules.seo.service import get_tags

    mock_response = [{"id": 5, "name": "vet", "slug": "vet"}]
    mocker.patch("src.modules.seo.service.wp_get", return_value=mock_response)

    result = await get_tags()
    assert len(result) == 1
    assert result[0]["slug"] == "vet"


@pytest.mark.asyncio
async def test_create_category(mocker: Any) -> None:
    """Test creating a new category.

    Args:
        mocker: Pytest mocker fixture.
    """
    from src.modules.seo.service import create_category

    mock_response = {"id": 10, "name": "New Category", "slug": "new-category"}
    mocker.patch("src.modules.seo.service.wp_post", return_value=mock_response)

    result = await create_category("New Category", slug="new-category")
    assert result["id"] == 10
    assert result["name"] == "New Category"
