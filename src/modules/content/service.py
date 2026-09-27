"""Content publishing service for article-writer integration."""

import logging
import re
from html import escape

import markdown as md  # type: ignore[import-untyped]

from src.config import WP_URL
from src.models import (
    BibliographyEntry,
    MediaResponse,
    PublishRequest,
    PublishResponse,
    VersoArticleRequest,
    VersoBibliographyEntry,
    VersoSection,
    WrittenSection,
)
from src.modules.articles.service import create_article
from src.modules.content.dropbox import download_dropbox_image
from src.modules.media.optimizer import optimize_image
from src.modules.media.uploader import upload_media

logger = logging.getLogger(__name__)

# WordPress base URL (strip /wp-json suffix)
_WP_BASE = WP_URL.replace("/wp-json", "")

# Map profile names to WordPress categories
PROFILE_CATEGORY_MAP: dict[str, str] = {
    "article_specialistes": "Spécialistes",
    "article_praticiens": "Praticiens",
    "fiche_info_proprietaire": "Propriétaires",
    "synthese_formation": "Formation",
    "livre_complet": "Livres",
}

# Heading shift pattern: shift headings down by 1 in section content
_HEADING_PATTERN = re.compile(r"^(#{1,5})\s", re.MULTILINE)


def _shift_heading_levels(content: str) -> str:
    """Shift markdown heading levels down by 1.

    Section titles are h2, so content headings start at h3.
    # → h2 (rare in section content), ## → h3, ### → h4.

    Args:
        content: Markdown content with headings.

    Returns:
        Content with heading levels shifted down by 1.
    """

    def _shift(match: re.Match) -> str:  # type: ignore[type-arg]
        hashes = match.group(1)
        new_level = min(len(hashes) + 1, 6)
        return "#" * new_level + " "

    return _HEADING_PATTERN.sub(_shift, content)


def _format_bibliography(entries: list[BibliographyEntry] | list[VersoBibliographyEntry]) -> str:
    """Format bibliography as HTML list.

    Args:
        entries: Bibliography entries.

    Returns:
        HTML-formatted bibliography.
    """
    if not entries:
        return ""

    items = "".join(f"<li>{escape(e.formatted)}</li>" for e in entries)
    return f'<h2 style="margin-top:40px">Bibliographie</h2><ol style="font-size:14px; line-height:1.8">{items}</ol>'


def _build_html_content(
    sections: list[WrittenSection],
    bibliography: list[BibliographyEntry],
    media_map: dict[str, MediaResponse],
    image_captions: dict[str, str],
) -> str:
    """Convert markdown sections to HTML with heading levels and images.

    Heading hierarchy:
    - Article title → WordPress post title (h1, not in content)
    - Section titles → h2
    - # in section markdown → h3
    - ## in section markdown → h4

    Args:
        sections: Article sections.
        bibliography: Bibliography entries.
        media_map: Mapping of attachment_key to uploaded media.
        image_captions: Mapping of attachment_key to caption text.

    Returns:
        Complete HTML content.
    """
    parts: list[str] = []

    for section in sections:
        # Section title as h2
        parts.append(f"<h2>{escape(section.title)}</h2>")

        # Clean content: remove CITE markers, shift heading levels
        clean_content = re.sub(r"\[CITE:[^\]]+\]", "", section.content)
        clean_content = _shift_heading_levels(clean_content)

        # Convert markdown to HTML
        html_section = md.markdown(clean_content, extensions=["extra"])
        parts.append(html_section)

        # Inject images for this section
        for attachment_key in section.selected_images:
            if media := media_map.get(attachment_key):
                caption = escape(image_captions.get(attachment_key, ""))
                alt = caption or "Image"
                parts.append(
                    '<figure style="text-align:center; margin:20px 0">'
                    f'<img src="{media.wp_url}" alt="{alt}" '
                    'style="max-width:100%; height:auto">'
                    f"<figcaption>{caption}</figcaption>"
                    "</figure>"
                )

    # Add bibliography
    parts.append(_format_bibliography(bibliography))

    return "\n".join(parts)


def _build_verso_html(
    sections: list[VersoSection],
    bibliography: list[VersoBibliographyEntry],
    media_map: dict[str, MediaResponse],
) -> str:
    """Convert verso-formatted sections to HTML.

    The verso format already has shifted heading levels and clean content.

    Args:
        sections: Verso sections with normalized content.
        bibliography: Bibliography entries.
        media_map: Mapping of attachment_key to uploaded media.

    Returns:
        Complete HTML content.
    """
    parts: list[str] = []

    for section in sections:
        # Section title as h2
        parts.append(f"<h2>{escape(section.title)}</h2>")

        # Content already has shifted headings and no CITE markers
        html_section = md.markdown(section.content, extensions=["extra"])
        parts.append(html_section)

        # Inject images for this section
        for img in section.images:
            if media := media_map.get(img.attachment_key):
                caption = escape(img.caption)
                alt = caption or "Image"
                parts.append(
                    '<figure style="text-align:center; margin:20px 0">'
                    f'<img src="{media.wp_url}" alt="{alt}" '
                    'style="max-width:100%; height:auto">'
                    f"<figcaption>{caption}</figcaption>"
                    "</figure>"
                )

    # Add bibliography
    parts.append(_format_bibliography(bibliography))

    return "\n".join(parts)


async def _download_and_upload_images(
    images: list[dict],
) -> tuple[dict[str, MediaResponse], int | None]:
    """Download images from Dropbox, optimize, and upload to WordPress.

    Args:
        images: List of dicts with attachment_key, dropbox_url, caption.

    Returns:
        Tuple of (media_map, featured_image_id).
    """
    media_map: dict[str, MediaResponse] = {}
    featured_image_id: int | None = None

    for img in images:
        attachment_key = img["attachment_key"]
        dropbox_url = img["dropbox_url"]
        caption = img.get("caption", "")

        try:
            img_bytes = await download_dropbox_image(dropbox_url)
            webp_bytes, filename = optimize_image(img_bytes, context="article")
            media = await upload_media(
                filename=filename,
                content=webp_bytes,
                alt_text=caption,
                title=caption,
            )
            media_map[attachment_key] = media

            if featured_image_id is None:
                featured_image_id = media.id

            logger.info("Uploaded image: %s → %s", attachment_key, media.id)
        except Exception as e:
            logger.warning("Image upload failed for %s: %s", attachment_key, e)

    return media_map, featured_image_id


async def publish_written_content(request: PublishRequest) -> PublishResponse:
    """Publish WrittenContent to WordPress.

    Orchestrates the full pipeline:
    1. Download and optimize images from Dropbox
    2. Upload to WordPress media library
    3. Convert markdown sections to HTML
    4. Publish article via WordPress REST API

    Args:
        request: Publish request with WrittenContent.

    Returns:
        PublishResponse with post details or error.
    """
    content = request.content
    category = PROFILE_CATEGORY_MAP.get(content.profile_name, "Actualité")

    # Build image info list and caption map
    image_list = [
        {
            "attachment_key": img.attachment_key,
            "dropbox_url": img.dropbox_url,
            "caption": img.caption,
        }
        for img in content.selected_images
    ]
    image_captions = {img.attachment_key: img.caption for img in content.selected_images}

    media_map, featured_image_id = await _download_and_upload_images(image_list)

    # Build HTML content with proper heading levels
    html_content = _build_html_content(content.sections, content.bibliography, media_map, image_captions)

    if request.preview_only:
        return PublishResponse(status="preview", preview_html=html_content, error_message=None)

    return await _create_wp_article(
        title=content.context.objective,
        html_content=html_content,
        status=request.status,
        category=category,
        media_map=media_map,
        featured_image_id=featured_image_id,
    )


async def publish_verso_article(request: VersoArticleRequest) -> PublishResponse:
    """Publish verso-formatted article to WordPress.

    Accepts the structured format from article-writer's verso_formatter.
    Heading levels are already normalized.

    Args:
        request: VersoArticleRequest with sections, bibliography, metadata.

    Returns:
        PublishResponse with post details or error.
    """
    # Collect all images from all sections
    image_list = [
        {
            "attachment_key": img.attachment_key,
            "dropbox_url": img.dropbox_url,
            "caption": img.caption,
        }
        for section in request.sections
        for img in section.images
    ]

    media_map, featured_image_id = await _download_and_upload_images(image_list)

    # Build HTML with verso-specific builder
    html_content = _build_verso_html(request.sections, request.bibliography, media_map)

    return await _create_wp_article(
        title=request.title,
        html_content=html_content,
        status=request.status,
        category=request.category,
        excerpt=request.excerpt,
        media_map=media_map,
        featured_image_id=featured_image_id,
    )


async def _create_wp_article(
    title: str,
    html_content: str,
    status: str,
    category: str,
    media_map: dict[str, MediaResponse],
    featured_image_id: int | None = None,
    excerpt: str | None = None,
) -> PublishResponse:
    """Create WordPress article with fallback to draft on error.

    Args:
        title: Article title.
        html_content: Full HTML content.
        status: Publication status.
        category: WordPress category name.
        media_map: Uploaded media map.
        featured_image_id: WordPress media ID for featured image.
        excerpt: Optional article excerpt.

    Returns:
        PublishResponse with post details.
    """
    wp_base = _WP_BASE

    try:
        article = await create_article(
            title=title,
            content=html_content,
            excerpt=excerpt,
            status=status,
            categories=[category],
            featured_image_id=featured_image_id,
        )

        return PublishResponse(
            post_id=article.id,
            url=article.link,
            status=article.status,
            featured_image_url=next((m.wp_url for m in media_map.values()), None),
            edit_url=f"{wp_base}/wp-admin/post.php?post={article.id}&action=edit",
            error_message=None,
        )
    except Exception as e:
        logger.error("Publication failed, saving as draft: %s", e)
        try:
            article = await create_article(
                title=title,
                content=html_content,
                excerpt=excerpt,
                status="draft",
                categories=[category],
                featured_image_id=featured_image_id,
            )
            return PublishResponse(
                post_id=article.id,
                url=article.link,
                status="draft",
                featured_image_url=next((m.wp_url for m in media_map.values()), None),
                edit_url=f"{wp_base}/wp-admin/post.php?post={article.id}&action=edit",
                error_message=str(e),
            )
        except Exception as e2:
            logger.error("Draft creation also failed: %s", e2)
            return PublishResponse(
                status="failed",
                preview_html=html_content,
                error_message=str(e2),
            )
