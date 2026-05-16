"""WordPress article management service."""

import logging
from typing import Any

from src.core.wp_client import wp_delete, wp_get, wp_patch, wp_post
from src.models import ArticleResponse

logger = logging.getLogger(__name__)


async def create_article(
    title: str,
    content: str,
    excerpt: str | None = None,
    status: str = "draft",
    categories: list[str] | None = None,
    tags: list[str] | None = None,
    featured_image_id: int | None = None,
) -> ArticleResponse:
    """Create a new WordPress article.

    Args:
        title: Article title.
        content: Article content (HTML).
        excerpt: Short excerpt.
        status: Post status (draft, publish, etc).
        categories: Category names (will be converted to IDs).
        tags: Tag names (will be converted to IDs).
        featured_image_id: Media ID for featured image.

    Returns:
        ArticleResponse with created article data.
    """
    categories = categories or []
    tags = tags or []

    # Convert category/tag names to IDs
    category_ids = await _get_category_ids(categories)
    tag_ids = await _get_tag_ids(tags)

    data = {
        "title": title,
        "content": content,
        "status": status,
        "categories": category_ids,
        "tags": tag_ids,
    }

    if excerpt:
        data["excerpt"] = excerpt

    if featured_image_id:
        data["featured_media"] = featured_image_id  # type: ignore[assignment]

    resp = await wp_post("/wp/v2/posts", json_data=data)

    return ArticleResponse(
        id=resp["id"],
        title=resp["title"]["rendered"],
        status=resp["status"],
        link=resp["link"],
        date=resp.get("date"),
        excerpt=resp.get("excerpt", {}).get("rendered"),
        categories=resp.get("categories", []),
        tags=resp.get("tags", []),
    )


async def update_article(
    post_id: int,
    title: str | None = None,
    content: str | None = None,
    excerpt: str | None = None,
    status: str | None = None,
    categories: list[str] | None = None,
    tags: list[str] | None = None,
) -> ArticleResponse:
    """Update an existing article.

    Args:
        post_id: WordPress post ID.
        title: New title (optional).
        content: New content (optional).
        excerpt: New excerpt (optional).
        status: New status (optional).
        categories: New category names (optional).
        tags: New tag names (optional).

    Returns:
        ArticleResponse with updated article data.
    """
    data = {}

    if title:
        data["title"] = title
    if content:
        data["content"] = content
    if excerpt:
        data["excerpt"] = excerpt
    if status:
        data["status"] = status

    if categories:
        data["categories"] = await _get_category_ids(categories)  # type: ignore[assignment]
    if tags:
        data["tags"] = await _get_tag_ids(tags)  # type: ignore[assignment]

    resp = await wp_patch(f"/wp/v2/posts/{post_id}", json_data=data)

    return ArticleResponse(
        id=resp["id"],
        title=resp["title"]["rendered"],
        status=resp["status"],
        link=resp["link"],
        date=resp.get("date"),
        excerpt=resp.get("excerpt", {}).get("rendered"),
        categories=resp.get("categories", []),
        tags=resp.get("tags", []),
    )


async def delete_article(post_id: int) -> bool:
    """Delete an article.

    Args:
        post_id: WordPress post ID.

    Returns:
        True if successful.
    """
    await wp_delete(f"/wp/v2/posts/{post_id}?force=true")
    logger.info(f"Deleted article: {post_id}")
    return True


async def publish_article(post_id: int) -> ArticleResponse:
    """Publish a draft article.

    Args:
        post_id: WordPress post ID.

    Returns:
        ArticleResponse with updated article.
    """
    return await update_article(post_id, status="publish")


async def get_article(post_id: int) -> ArticleResponse:
    """Get a single article.

    Args:
        post_id: WordPress post ID.

    Returns:
        ArticleResponse with article data.
    """
    resp = await wp_get(
        f"/wp/v2/posts/{post_id}",
        params={"_fields": "id,title,content,excerpt,status,date,link,categories,tags"},
    )

    assert isinstance(resp, dict), "Expected dict response from wp_get"

    return ArticleResponse(
        id=resp["id"],
        title=resp["title"]["rendered"] if isinstance(resp["title"], dict) else resp["title"],
        status=resp["status"],
        link=resp["link"],
        date=resp.get("date"),
        excerpt=resp.get("excerpt", {}).get("rendered")
        if isinstance(resp.get("excerpt"), dict)
        else resp.get("excerpt"),
        categories=resp.get("categories", []),
        tags=resp.get("tags", []),
    )


async def list_articles(status: str = "publish", limit: int = 10, search: str = "") -> list[dict[str, Any]]:
    """List articles.

    Args:
        status: Filter by status.
        limit: Number of articles to return.
        search: Search keyword.

    Returns:
        List of article data.
    """
    params = {"per_page": limit, "status": status}

    if search:
        params["search"] = search

    resp = await wp_get("/wp/v2/posts", params=params)

    if not isinstance(resp, list):
        return []

    return [
        {
            "id": article["id"],
            "title": article.get("title", {}).get("rendered", ""),
            "status": article.get("status"),
            "date": article.get("date"),
            "link": article.get("link"),
        }
        for article in resp
    ]


async def _get_category_ids(category_names: list[str]) -> list[int]:
    """Convert category names to IDs.

    Args:
        category_names: List of category names.

    Returns:
        List of category IDs.
    """
    if not category_names:
        return []

    categories = await wp_get("/wp/v2/categories", params={"per_page": 100, "_fields": "id,name"})

    if not isinstance(categories, list):
        return []

    category_map = {cat["name"]: cat["id"] for cat in categories}
    return [category_map[name] for name in category_names if name in category_map]


async def _get_tag_ids(tag_names: list[str]) -> list[int]:
    """Convert tag names to IDs.

    Args:
        tag_names: List of tag names.

    Returns:
        List of tag IDs.
    """
    if not tag_names:
        return []

    tags = await wp_get("/wp/v2/tags", params={"per_page": 100, "_fields": "id,name"})

    if not isinstance(tags, list):
        return []

    tag_map = {tag["name"]: tag["id"] for tag in tags}
    return [tag_map[name] for name in tag_names if name in tag_map]
