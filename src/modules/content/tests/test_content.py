"""Tests for content publishing module."""

from typing import Any

import pytest

from src.models import (
    ArticleResponse,
    BibliographyEntry,
    MediaResponse,
    PublishRequest,
    RedactionContext,
    VersoArticleRequest,
    VersoBibliographyEntry,
    VersoMetadata,
    VersoSection,
    VersoSectionImage,
    WrittenContent,
    WrittenContentMetadata,
    WrittenSection,
)


@pytest.mark.asyncio
async def test_publish_content_preview(mocker: Any) -> None:
    """Test preview mode (no publishing).

    Args:
        mocker: Pytest mocker fixture.
    """
    from src.modules.content.service import publish_written_content

    # Mock _download_and_upload_images to avoid network calls
    mocker.patch(
        "src.modules.content.service._download_and_upload_images",
        return_value=({}, None),
    )

    content = WrittenContent(
        id="test-1",
        package_id="pkg-1",
        profile_name="article_specialistes",
        context=RedactionContext(
            objective="Test Article",
            target_audience="Specialists",
            word_count_target=2000,
        ),
        sections=[
            WrittenSection(
                id="sec-1",
                title="Introduction",
                content="Test content [CITE:key1]",
                word_count=100,
                references_used=["key1"],
                selected_images=[],
            )
        ],
        selected_images=[],
        bibliography=[BibliographyEntry(zotero_key="key1", formatted="Author et al. (2024)")],
        metadata=WrittenContentMetadata(
            total_words=100,
            total_images=0,
            profile_used="article_specialistes",
            generation_time_ms=1500.0,
        ),
    )

    request = PublishRequest(content=content, preview_only=True)
    response = await publish_written_content(request)

    assert response.status == "preview"
    assert response.preview_html is not None
    assert "Introduction" in response.preview_html
    assert "Bibliographie" in response.preview_html


@pytest.mark.asyncio
async def test_publish_content_draft(mocker: Any) -> None:
    """Test publishing as draft.

    Args:
        mocker: Pytest mocker fixture.
    """
    from src.modules.content.service import publish_written_content

    # Mock image pipeline
    mocker.patch(
        "src.modules.content.service._download_and_upload_images",
        return_value=({}, None),
    )

    # Mock article creation
    mock_article = ArticleResponse(
        id=999,
        title="Test Article",
        status="draft",
        link="https://verso-vet.com/?p=999",
    )
    mocker.patch(
        "src.modules.content.service.create_article",
        return_value=mock_article,
    )

    content = WrittenContent(
        id="test-2",
        package_id="pkg-2",
        profile_name="article_praticiens",
        context=RedactionContext(
            objective="Test Article",
            target_audience="Practitioners",
            word_count_target=1500,
        ),
        sections=[
            WrittenSection(
                id="sec-1",
                title="Section",
                content="Content",
                word_count=100,
                selected_images=[],
            )
        ],
        selected_images=[],
        bibliography=[],
        metadata=WrittenContentMetadata(
            total_words=100,
            total_images=0,
            profile_used="article_praticiens",
            generation_time_ms=1000.0,
        ),
    )

    request = PublishRequest(content=content, status="draft")
    response = await publish_written_content(request)

    assert response.post_id == 999
    assert response.status == "draft"
    assert response.url is not None and "verso-vet.com" in response.url


def test_format_bibliography() -> None:
    """Test bibliography formatting uses h2 and ol tags."""
    from src.modules.content.service import _format_bibliography

    entries: list[BibliographyEntry] = [
        BibliographyEntry(zotero_key="key1", formatted="Author A (2024) Title. Journal."),
        BibliographyEntry(zotero_key="key2", formatted="Author B (2023) Other. Magazine."),
    ]

    html: str = _format_bibliography(entries)

    assert "<h2" in html
    assert "Bibliographie" in html
    assert "<ol" in html
    assert "Author A (2024)" in html
    assert "Author B (2023)" in html
    # Verify old tags are NOT present
    assert "<h3" not in html
    assert "<ul" not in html


def test_format_bibliography_empty() -> None:
    """Test bibliography formatting with empty list returns empty string."""
    from src.modules.content.service import _format_bibliography

    html: str = _format_bibliography([])
    assert html == ""


def test_build_html_content() -> None:
    """Test HTML content building with image_captions argument."""
    from src.modules.content.service import _build_html_content

    sections: list[WrittenSection] = [
        WrittenSection(
            id="sec-1",
            title="First Section",
            content="# Heading\n\nParagraph [CITE:key1]",
            word_count=50,
            selected_images=["img-1"],
        ),
        WrittenSection(
            id="sec-2",
            title="Second Section",
            content="More content without citations",
            word_count=50,
            selected_images=[],
        ),
    ]

    bibliography: list[BibliographyEntry] = [BibliographyEntry(zotero_key="key1", formatted="Source (2024)")]

    media_map: dict[str, MediaResponse] = {
        "img-1": MediaResponse(
            id=123,
            wp_url="https://verso-vet.com/wp-content/uploads/img.webp",
            filename="img.webp",
            size=45000,
        )
    }

    image_captions: dict[str, str] = {
        "img-1": "A descriptive caption",
    }

    html: str = _build_html_content(sections, bibliography, media_map, image_captions)

    assert "<h2>First Section</h2>" in html
    assert "<h2>Second Section</h2>" in html
    assert "[CITE:" not in html  # Citations removed
    assert "verso-vet.com/wp-content/uploads" in html  # Image included
    assert "A descriptive caption" in html  # Caption rendered
    assert "Bibliographie" in html


def test_shift_heading_levels() -> None:
    """Test that _shift_heading_levels shifts markdown headings down by 1.

    Verifies:
        - ## becomes ### (shift by 1)
        - ### becomes #### (shift by 1)
        - # becomes ## (shift by 1)
        - Plain text without headings is unchanged
    """
    from src.modules.content.service import _shift_heading_levels

    assert _shift_heading_levels("## Heading") == "### Heading"
    assert _shift_heading_levels("### Sub") == "#### Sub"
    assert _shift_heading_levels("# Title") == "## Title"

    plain: str = "This is plain text without headings."
    assert _shift_heading_levels(plain) == plain


def test_build_html_heading_hierarchy() -> None:
    """Test that _build_html_content produces correct heading hierarchy.

    Verifies:
        - Section title renders as h2
        - ## in content renders as h3 (shifted from ## to ###)
        - ### in content renders as h4 (shifted from ### to ####)
        - [CITE:key] markers are removed from output
    """
    from src.modules.content.service import _build_html_content

    sections: list[WrittenSection] = [
        WrittenSection(
            id="sec-1",
            title="Section Title",
            content="## Sub Heading\n\nSome text [CITE:ref1]\n\n### Deep Heading\n\nMore text",
            word_count=20,
            selected_images=[],
        ),
    ]

    bibliography: list[BibliographyEntry] = []
    media_map: dict[str, MediaResponse] = {}
    image_captions: dict[str, str] = {}

    html: str = _build_html_content(sections, bibliography, media_map, image_captions)

    # Section title as h2
    assert "<h2>Section Title</h2>" in html
    # ## shifted to ### renders as h3
    assert "<h3>" in html
    assert "Sub Heading" in html
    # ### shifted to #### renders as h4
    assert "<h4>" in html
    assert "Deep Heading" in html
    # CITE markers removed
    assert "[CITE:" not in html


def test_build_verso_html() -> None:
    """Test _build_verso_html with VersoSection objects.

    Verifies:
        - Section titles render as h2
        - Section content is rendered as HTML
        - Images are injected with correct captions
    """
    from src.modules.content.service import _build_verso_html

    sections: list[VersoSection] = [
        VersoSection(
            id="vs-1",
            title="Verso Section",
            content="Paragraph of **bold** text.\n\n### Sub heading\n\nMore details here.",
            images=[
                VersoSectionImage(
                    attachment_key="img-v1",
                    dropbox_url="https://dropbox.com/fake",
                    caption="Verso image caption",
                ),
            ],
        ),
    ]

    bibliography: list[VersoBibliographyEntry] = [
        VersoBibliographyEntry(zotero_key="vk1", formatted="Verso Author (2025) Paper."),
    ]

    media_map: dict[str, MediaResponse] = {
        "img-v1": MediaResponse(
            id=456,
            wp_url="https://verso-vet.com/wp-content/uploads/verso-img.webp",
            filename="verso-img.webp",
            size=30000,
        ),
    }

    html: str = _build_verso_html(sections, bibliography, media_map)

    # Section title as h2
    assert "<h2>Verso Section</h2>" in html
    # Content rendered (bold text)
    assert "<strong>bold</strong>" in html
    # Image injected with caption
    assert "verso-vet.com/wp-content/uploads/verso-img.webp" in html
    assert "Verso image caption" in html
    # Bibliography present
    assert "Bibliographie" in html
    assert "Verso Author (2025)" in html


@pytest.mark.asyncio
async def test_publish_verso_article_preview(mocker: Any) -> None:
    """Test publish_verso_article creates article and returns correct response.

    Args:
        mocker: Pytest mocker fixture.
    """
    from src.modules.content.service import publish_verso_article

    # Mock image pipeline
    mocker.patch(
        "src.modules.content.service._download_and_upload_images",
        return_value=({}, None),
    )

    # Mock article creation
    mock_article = ArticleResponse(
        id=1001,
        title="Verso Test Article",
        status="draft",
        link="https://verso-vet.com/?p=1001",
    )
    mocker.patch(
        "src.modules.content.service.create_article",
        return_value=mock_article,
    )

    request = VersoArticleRequest(
        title="Verso Test Article",
        excerpt="Test excerpt",
        category="Praticiens",
        status="draft",
        sections=[
            VersoSection(
                id="vs-1",
                title="Intro",
                content="Test verso content",
                images=[],
            ),
        ],
        bibliography=[],
        metadata=VersoMetadata(
            total_words=50,
            profile_used="article_praticiens",
            source_content_id="wc-1",
            source_package_id="pkg-1",
        ),
    )

    response = await publish_verso_article(request)

    assert response.post_id == 1001
    assert response.status == "draft"
    assert response.url is not None and "verso-vet.com" in response.url
