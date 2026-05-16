"""Tests for article builder module."""

from typing import Any

from src.modules.articles.builder import build_html


def test_build_html_hero_block() -> None:
    """Test building hero block to HTML."""
    blocks = [{"type": "hero", "text": "Welcome", "image_url": None}]
    html = build_html(blocks)
    assert "Welcome" in html
    assert "hero" in html.lower() or "padding" in html


def test_build_html_text_block() -> None:
    """Test building text block to HTML."""
    blocks = [{"type": "text", "heading": "Title", "content": "<p>Content</p>"}]
    html = build_html(blocks)
    assert "Title" in html
    assert "<p>Content</p>" in html


def test_build_html_image_block() -> None:
    """Test building image block to HTML."""
    blocks = [
        {
            "type": "image",
            "url": "http://example.com/image.jpg",
            "alt": "Test image",
        }
    ]
    html = build_html(blocks)
    assert "http://example.com/image.jpg" in html
    assert "Test image" in html


def test_build_html_list_block() -> None:
    """Test building list block to HTML."""
    blocks = [{"type": "list", "items": ["Item 1", "Item 2", "Item 3"]}]
    html = build_html(blocks)
    assert "Item 1" in html
    assert "Item 2" in html
    assert "<ul" in html and "<li" in html


def test_build_html_video_block() -> None:
    """Test building video block to HTML."""
    blocks = [{"type": "video", "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}]
    html = build_html(blocks)
    assert "youtube.com/embed" in html or "iframe" in html


def test_build_html_cta_block() -> None:
    """Test building CTA block to HTML."""
    blocks = [{"type": "cta", "text": "Click here", "url": "/action"}]
    html = build_html(blocks)
    assert "Click here" in html
    assert "/action" in html
    assert "<a" in html


def test_build_html_quote_block() -> None:
    """Test building quote block to HTML."""
    blocks = [
        {
            "type": "quote",
            "text": "This is a quote",
            "author": "Someone",
        }
    ]
    html = build_html(blocks)
    assert "This is a quote" in html
    assert "Someone" in html
    assert "blockquote" in html


def test_build_html_multiple_blocks() -> None:
    """Test building multiple blocks together."""
    blocks: list[dict[str, Any]] = [
        {"type": "hero", "text": "Title"},
        {"type": "text", "heading": "Section 1", "content": "<p>Content</p>"},
        {"type": "list", "items": ["Point 1", "Point 2"]},
    ]
    html = build_html(blocks)
    assert "Title" in html
    assert "Section 1" in html
    assert "Point 1" in html
