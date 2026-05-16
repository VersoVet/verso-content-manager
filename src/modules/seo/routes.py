"""FastAPI routes for SEO and taxonomy management."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from src.modules.seo.service import (
    create_category,
    create_tag,
    get_categories,
    get_tags,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/seo", tags=["seo"])


@router.get("/categories", response_model=list[dict[str, Any]])
async def list_categories_endpoint() -> list[dict[str, Any]]:
    """Get all categories.

    Returns:
        List of categories with id, name, slug.
    """
    try:
        categories = await get_categories()
        return categories
    except Exception as e:
        logger.error(f"Failed to list categories: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/categories", response_model=dict[str, Any])
async def create_category_endpoint(name: str, slug: str | None = None) -> dict[str, Any]:
    """Create a new category.

    Args:
        name: Category name.
        slug: Optional slug.

    Returns:
        Created category data.
    """
    try:
        category = await create_category(name, slug)
        logger.info(f"Created category: {category['name']}")
        return category
    except Exception as e:
        logger.error(f"Failed to create category: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tags", response_model=list[dict[str, Any]])
async def list_tags_endpoint() -> list[dict[str, Any]]:
    """Get all tags.

    Returns:
        List of tags with id, name, slug.
    """
    try:
        tags = await get_tags()
        return tags
    except Exception as e:
        logger.error(f"Failed to list tags: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tags", response_model=dict[str, Any])
async def create_tag_endpoint(name: str, slug: str | None = None) -> dict[str, Any]:
    """Create a new tag.

    Args:
        name: Tag name.
        slug: Optional slug.

    Returns:
        Created tag data.
    """
    try:
        tag = await create_tag(name, slug)
        logger.info(f"Created tag: {tag['name']}")
        return tag
    except Exception as e:
        logger.error(f"Failed to create tag: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
