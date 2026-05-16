"""SEO and taxonomy management service."""

import logging
from typing import Any

from src.core.wp_client import wp_get, wp_post

logger = logging.getLogger(__name__)


async def get_categories() -> list[dict[str, Any]]:
    """Fetch all categories from WordPress.

    Returns:
        List of category dictionaries with id, name, slug.
    """
    try:
        categories = await wp_get("/wp/v2/categories", params={"per_page": 100, "_fields": "id,name,slug"})

        if not isinstance(categories, list):
            return []

        return [{"id": cat["id"], "name": cat["name"], "slug": cat.get("slug", "")} for cat in categories]
    except Exception as e:
        logger.error(f"Failed to fetch categories: {str(e)}")
        return []


async def get_tags() -> list[dict[str, Any]]:
    """Fetch all tags from WordPress.

    Returns:
        List of tag dictionaries with id, name, slug.
    """
    try:
        tags = await wp_get("/wp/v2/tags", params={"per_page": 100, "_fields": "id,name,slug"})

        if not isinstance(tags, list):
            return []

        return [{"id": tag["id"], "name": tag["name"], "slug": tag.get("slug", "")} for tag in tags]
    except Exception as e:
        logger.error(f"Failed to fetch tags: {str(e)}")
        return []


async def create_category(name: str, slug: str | None = None) -> dict[str, Any]:
    """Create a new category in WordPress.

    Args:
        name: Category name.
        slug: Optional slug (auto-generated if not provided).

    Returns:
        Category data with id, name, slug.

    Raises:
        ValueError: If creation fails.
    """
    try:
        data = {"name": name}
        if slug:
            data["slug"] = slug

        resp = await wp_post("/wp/v2/categories", json_data=data)

        logger.info(f"Created category: {resp['id']} ({name})")
        return {"id": resp["id"], "name": resp["name"], "slug": resp.get("slug", "")}
    except Exception as e:
        logger.error(f"Failed to create category: {str(e)}")
        raise ValueError(f"Failed to create category: {str(e)}")


async def create_tag(name: str, slug: str | None = None) -> dict[str, Any]:
    """Create a new tag in WordPress.

    Args:
        name: Tag name.
        slug: Optional slug (auto-generated if not provided).

    Returns:
        Tag data with id, name, slug.

    Raises:
        ValueError: If creation fails.
    """
    try:
        data = {"name": name}
        if slug:
            data["slug"] = slug

        resp = await wp_post("/wp/v2/tags", json_data=data)

        logger.info(f"Created tag: {resp['id']} ({name})")
        return {"id": resp["id"], "name": resp["name"], "slug": resp.get("slug", "")}
    except Exception as e:
        logger.error(f"Failed to create tag: {str(e)}")
        raise ValueError(f"Failed to create tag: {str(e)}")
