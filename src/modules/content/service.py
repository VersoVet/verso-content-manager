"""Content publishing service for article-writer integration."""

import logging
import re

import markdown as md  # type: ignore[import-untyped]

from src.models import (
    BibliographyEntry,
    MediaResponse,
    PublishRequest,
    PublishResponse,
    WrittenSection,
)
from src.modules.articles.service import create_article
from src.modules.content.dropbox import download_dropbox_image
from src.modules.media.optimizer import optimize_image
from src.modules.media.uploader import upload_media

logger = logging.getLogger(__name__)

# Map profile names to WordPress categories
PROFILE_CATEGORY_MAP: dict[str, str] = {
    "article_specialistes": "Spécialistes",
    "article_praticiens": "Praticiens",
    "fiche_info_proprietaire": "Propriétaires",
    "synthese_formation": "Formation",
    "livre_complet": "Livres",
}


def _format_bibliography(entries: list[BibliographyEntry]) -> str:
    """Format bibliography as HTML list.

    Args:
        entries: Bibliography entries.

    Returns:
        HTML-formatted bibliography.
    """
    if not entries:
        return ""

    items = "".join(f"<li>{e.formatted}</li>" for e in entries)
    style = 'style="font-size:14px; line-height:1.8; margin-top:20px"'
    return f"<h3>Bibliographie</h3><ul {style}>{items}</ul>"


def _build_html_content(
    sections: list[WrittenSection],
    bibliography: list[BibliographyEntry],
    media_map: dict[str, MediaResponse],
) -> str:
    """Convert markdown sections to HTML with embedded images and bibliography.

    Args:
        sections: Article sections.
        bibliography: Bibliography entries.
        media_map: Mapping of attachment_key to uploaded media.

    Returns:
        Complete HTML content.
    """
    parts: list[str] = []

    for section in sections:
        # Add section heading
        parts.append(f"<h2>{section.title}</h2>")

        # Convert markdown to HTML, remove [CITE:...] markers
        clean_content = re.sub(r"\[CITE:[^\]]+\]", "", section.content)
        html_section = md.markdown(clean_content)
        parts.append(html_section)

        # Inject images for this section
        for attachment_key in section.selected_images:
            if media := media_map.get(attachment_key):
                # Find the SelectedImage to get caption
                caption = attachment_key  # fallback
                parts.append(
                    f'<figure style="text-align:center; margin:20px 0">'
                    f'<img src="{media.wp_url}" alt="{caption}" '
                    f'style="max-width:100%; height:auto">'
                    f"<figcaption>{caption}</figcaption>"
                    f"</figure>"
                )

    # Add bibliography
    parts.append(_format_bibliography(bibliography))

    return "\n".join(parts)


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

    # Map profile to category
    category = PROFILE_CATEGORY_MAP.get(content.profile_name, "Actualité")

    # Download and upload images
    media_map: dict[str, MediaResponse] = {}
    featured_image_id: int | None = None

    for img in content.selected_images:
        try:
            # Download from Dropbox
            img_bytes = await download_dropbox_image(img.dropbox_url)

            # Optimize to WebP
            webp_bytes, filename = optimize_image(img_bytes, context="article")

            # Upload to WordPress
            media = await upload_media(
                filename=filename,
                content=webp_bytes,
                alt_text=img.caption,
                title=img.caption,
            )
            media_map[img.attachment_key] = media

            # Set first image as featured
            if featured_image_id is None:
                featured_image_id = media.id

            logger.info(f"Uploaded image: {img.attachment_key} → {media.id}")
        except Exception as e:
            logger.warning(f"Image upload failed for {img.attachment_key}: {e}")

    # Build HTML content
    html_content = _build_html_content(
        content.sections, content.bibliography, media_map
    )

    # Preview only?
    if request.preview_only:
        return PublishResponse(
            status="preview", preview_html=html_content, error_message=None
        )

    # Create article
    try:
        article = await create_article(
            title=content.context.objective,
            content=html_content,
            status=request.status,
            categories=[category],
        )

        wp_base = "https://verso-vet.com"
        return PublishResponse(
            post_id=article.id,
            url=article.link,
            status=article.status,
            featured_image_url=next(
                (m.wp_url for m in media_map.values()), None
            ),
            edit_url=f"{wp_base}/wp-admin/post.php?post={article.id}&action=edit",
            error_message=None,
        )
    except Exception as e:
        # Fallback to draft on error
        logger.error(f"Publication failed, saving as draft: {e}")
        try:
            article = await create_article(
                title=content.context.objective,
                content=html_content,
                status="draft",
                categories=[category],
            )
            wp_base = "https://verso-vet.com"
            return PublishResponse(
                post_id=article.id,
                url=article.link,
                status="draft",
                featured_image_url=next(
                    (m.wp_url for m in media_map.values()), None
                ),
                edit_url=f"{wp_base}/wp-admin/post.php?post={article.id}&action=edit",
                error_message=str(e),
            )
        except Exception as e2:
            logger.error(f"Draft creation also failed: {e2}")
            return PublishResponse(
                status="failed",
                preview_html=html_content,
                error_message=str(e2),
            )
