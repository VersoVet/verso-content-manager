"""FastAPI routes for article management."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from src.models import ArticleRequest, ArticleResponse
from src.modules.articles.builder import build_html
from src.modules.articles.service import (
    create_article,
    delete_article,
    get_article,
    list_articles,
    publish_article,
    update_article,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/articles", tags=["articles"])


@router.post("", response_model=ArticleResponse)
async def create_article_endpoint(request: ArticleRequest) -> ArticleResponse:
    """Create a new article from JSON blocks.

    Args:
        request: ArticleRequest with blocks and metadata.

    Returns:
        ArticleResponse with created article data.
    """
    try:
        # Convert blocks to HTML
        html_content = build_html(request.blocks)

        # Create article
        article = await create_article(
            title=request.title,
            content=html_content,
            excerpt=request.excerpt,
            status=request.status,
            categories=request.categories,
            tags=request.tags,
        )

        logger.info(f"Created article: {article.id} ({request.title})")
        return article
    except Exception as e:
        logger.error(f"Failed to create article: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=list[dict[str, Any]])
async def list_articles_endpoint(
    status: str = "publish", limit: int = 10, search: str = ""
) -> list[dict[str, Any]]:
    """List articles with optional filtering.

    Args:
        status: Filter by status (publish, draft, etc).
        limit: Max articles to return.
        search: Search keyword.

    Returns:
        List of articles.
    """
    try:
        articles = await list_articles(status=status, limit=limit, search=search)
        return articles
    except Exception as e:
        logger.error(f"Failed to list articles: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{post_id}", response_model=ArticleResponse)
async def get_article_endpoint(post_id: int) -> ArticleResponse:
    """Get a single article.

    Args:
        post_id: WordPress post ID.

    Returns:
        ArticleResponse with article data.
    """
    try:
        article = await get_article(post_id)
        return article
    except Exception as e:
        logger.error(f"Failed to get article {post_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{post_id}", response_model=ArticleResponse)
async def update_article_endpoint(post_id: int, request: ArticleRequest) -> ArticleResponse:
    """Update an article.

    Args:
        post_id: WordPress post ID.
        request: Updated article data.

    Returns:
        ArticleResponse with updated article.
    """
    try:
        # Convert blocks to HTML if provided
        html_content = None
        if request.blocks:
            html_content = build_html(request.blocks)

        article = await update_article(
            post_id,
            title=request.title,
            content=html_content,
            excerpt=request.excerpt,
            status=request.status,
            categories=request.categories,
            tags=request.tags,
        )

        logger.info(f"Updated article: {post_id}")
        return article
    except Exception as e:
        logger.error(f"Failed to update article {post_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{post_id}", response_model=dict[str, str])
async def delete_article_endpoint(post_id: int) -> dict[str, str]:
    """Delete an article.

    Args:
        post_id: WordPress post ID.

    Returns:
        Success message.
    """
    try:
        await delete_article(post_id)
        return {"message": f"Article {post_id} deleted"}
    except Exception as e:
        logger.error(f"Failed to delete article {post_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{post_id}/publish", response_model=ArticleResponse)
async def publish_article_endpoint(post_id: int) -> ArticleResponse:
    """Publish a draft article.

    Args:
        post_id: WordPress post ID.

    Returns:
        ArticleResponse with published article.
    """
    try:
        article = await publish_article(post_id)
        logger.info(f"Published article: {post_id}")
        return article
    except Exception as e:
        logger.error(f"Failed to publish article {post_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
