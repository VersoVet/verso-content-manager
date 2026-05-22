"""Convert JSON blocks to HTML styled for Verso Vet."""

import logging
from typing import Any

from src.config import COLOR_ACCENT, COLOR_PRIMARY

logger = logging.getLogger(__name__)


def build_html(blocks: list[dict[str, Any]]) -> str:
    """Convert block structure to HTML.

    Args:
        blocks: List of block dictionaries.

    Returns:
        Complete HTML content styled for Verso Vet.
    """
    html_parts = []

    for block in blocks:
        block_type = block.get("type")

        if block_type == "hero":
            html_parts.append(_build_hero(block))
        elif block_type == "text":
            html_parts.append(_build_text(block))
        elif block_type == "image":
            html_parts.append(_build_image(block))
        elif block_type == "two_columns":
            html_parts.append(_build_two_columns(block))
        elif block_type == "three_columns":
            html_parts.append(_build_three_columns(block))
        elif block_type == "list":
            html_parts.append(_build_list(block))
        elif block_type == "video":
            html_parts.append(_build_video(block))
        elif block_type == "cta":
            html_parts.append(_build_cta(block))
        elif block_type == "quote":
            html_parts.append(_build_quote(block))

    return "\n".join(html_parts)


def _build_hero(block: dict[str, Any]) -> str:
    """Build full-width hero section with background color.

    Args:
        block: Block dict with 'text' and optional 'image_url'.

    Returns:
        HTML string for hero section.
    """
    text = block.get("text", "")
    image = block.get("image_url", "")

    html = f'<div style="background: {COLOR_PRIMARY}; color: white; padding: 80px 30px; text-align: center;">'

    if image:
        html += f'<img src="{image}" alt="Hero" style="max-width: 100%; height: auto; margin-bottom: 20px;">'

    html += f'<h1 style="font-size: 48px; font-weight: 700; margin: 20px 0;">{text}</h1>'
    html += "</div>"

    return html


def _build_text(block: dict[str, Any]) -> str:
    """Build text section with optional heading and content.

    Args:
        block: Block dict with 'content' and optional 'heading'.

    Returns:
        HTML string for text section.
    """
    heading = block.get("heading")
    content = block.get("content", "")

    html = '<div style="padding: 30px; line-height: 1.8;">'

    if heading:
        html += f'<h2 style="font-size: 28px; color: {COLOR_PRIMARY}; font-weight: 700; margin-bottom: 20px;">{heading}</h2>'

    html += f'<div style="font-size: 16px; color: #333;">{content}</div>'
    html += "</div>"

    return html


def _build_image(block: dict[str, Any]) -> str:
    """Build centered image section with optional caption.

    Args:
        block: Block dict with 'url', 'alt', optional 'caption'.

    Returns:
        HTML string for image section.
    """
    url = block.get("url", "")
    alt = block.get("alt", "Image")
    caption = block.get("caption", "")

    html = '<div style="text-align: center; padding: 30px;">'
    html += f'<figure><img src="{url}" alt="{alt}" style="max-width: 100%; height: auto; border-radius: 8px;"/>'

    if caption:
        html += f'<figcaption style="font-size: 14px; color: #666; margin-top: 10px;">{caption}</figcaption>'

    html += "</figure></div>"

    return html


def _build_two_columns(block: dict[str, Any]) -> str:
    """Build two-column responsive grid layout.

    Args:
        block: Block dict with 'left' and 'right' nested blocks.

    Returns:
        HTML string for two-column layout.
    """
    left = block.get("left", {})
    right = block.get("right", {})

    left_html = build_html([left]) if left else ""
    right_html = build_html([right]) if right else ""

    html = '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; padding: 30px;">'
    html += f"<div>{left_html}</div>"
    html += f"<div>{right_html}</div>"
    html += "</div>"

    return html


def _build_three_columns(block: dict[str, Any]) -> str:
    """Build three-column responsive grid layout.

    Args:
        block: Block dict with 'columns' array of 3 nested blocks.

    Returns:
        HTML string for three-column layout.
    """
    columns = block.get("columns", [])

    html = '<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 30px; padding: 30px;">'

    for col in columns:
        col_html = build_html([col]) if col else ""
        html += f"<div>{col_html}</div>"

    html += "</div>"

    return html


def _build_list(block: dict[str, Any]) -> str:
    """Build unordered list from items array.

    Args:
        block: Block dict with 'items' array of strings.

    Returns:
        HTML string for unordered list.
    """
    items = block.get("items", [])

    html = '<div style="padding: 30px;">'
    html += '<ul style="font-size: 16px; line-height: 1.8; margin-left: 20px;">'

    for item in items:
        html += f'<li style="margin-bottom: 10px;">{item}</li>'

    html += "</ul></div>"

    return html


def _build_video(block: dict[str, Any]) -> str:
    """Build embedded video from YouTube or Vimeo URL.

    Args:
        block: Block dict with 'url' to YouTube or Vimeo video.

    Returns:
        HTML string for embedded video iframe.
    """
    url = block.get("url", "")

    # Extract video ID from URL
    video_id = ""
    if "youtube.com" in url or "youtu.be" in url:
        if "v=" in url:
            video_id = url.split("v=")[1].split("&")[0]
        else:
            video_id = url.split("/")[-1]
        embed_url = f"https://www.youtube.com/embed/{video_id}"
    elif "vimeo.com" in url:
        video_id = url.split("/")[-1]
        embed_url = f"https://player.vimeo.com/video/{video_id}"
    else:
        return ""

    html = f'<div style="padding: 30px; text-align: center;"><iframe width="100%" height="500" src="{embed_url}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></div>'

    return html


def _build_cta(block: dict[str, Any]) -> str:
    """Build call-to-action button with link.

    Args:
        block: Block dict with 'text' (button label) and 'url' (link target).

    Returns:
        HTML string for CTA button.
    """
    text = block.get("text", "Cliquer")
    url = block.get("url", "/")

    html = f'<div style="padding: 50px 30px; text-align: center;"><a href="{url}" style="display: inline-block; background: {COLOR_PRIMARY}; color: white; padding: 15px 40px; text-decoration: none; border-radius: 5px; font-weight: 700; font-size: 16px;">{text}</a></div>'

    return html


def _build_quote(block: dict[str, Any]) -> str:
    """Build blockquote section with optional author attribution.

    Args:
        block: Block dict with 'text' (quote) and optional 'author'.

    Returns:
        HTML string for blockquote.
    """
    text = block.get("text", "")
    author = block.get("author", "")

    html = f'<div style="border-left: 4px solid {COLOR_ACCENT}; padding: 30px; background: #f9f9f9; margin: 30px;">'
    html += f'<blockquote style="font-size: 18px; font-style: italic; color: #333; margin: 0;">{text}</blockquote>'

    if author:
        html += f'<p style="font-size: 14px; color: #666; margin-top: 10px;">— {author}</p>'

    html += "</div>"

    return html
