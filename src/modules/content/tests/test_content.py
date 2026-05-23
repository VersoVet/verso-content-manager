"""Tests for content publishing module."""

from typing import Any

import pytest

from src.models import (
    BibliographyEntry,
    PublishRequest,
    RedactionContext,
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
        bibliography=[
            BibliographyEntry(zotero_key="key1", formatted="Author et al. (2024)")
        ],
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
    from src.models import ArticleResponse
    from src.modules.content.service import publish_written_content

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
    """Test bibliography formatting.

    Args:
        None.

    Returns:
        None.
    """
    from src.modules.content.service import _format_bibliography

    entries = [
        BibliographyEntry(
            zotero_key="key1", formatted="Author A (2024) Title. Journal."
        ),
        BibliographyEntry(
            zotero_key="key2", formatted="Author B (2023) Other. Magazine."
        ),
    ]

    html = _format_bibliography(entries)

    assert "<h3>Bibliographie</h3>" in html
    assert "<ul" in html
    assert "Author A (2024)" in html
    assert "Author B (2023)" in html


def test_build_html_content() -> None:
    """Test HTML content building.

    Args:
        None.

    Returns:
        None.
    """
    from src.models import MediaResponse
    from src.modules.content.service import _build_html_content

    sections = [
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

    bibliography = [
        BibliographyEntry(zotero_key="key1", formatted="Source (2024)")
    ]

    media_map = {
        "img-1": MediaResponse(
            id=123,
            wp_url="https://verso-vet.com/wp-content/uploads/img.webp",
            filename="img.webp",
            size=45000,
        )
    }

    html = _build_html_content(sections, bibliography, media_map)

    assert "<h2>First Section</h2>" in html
    assert "<h2>Second Section</h2>" in html
    assert "[CITE:" not in html  # Citations removed
    assert "verso-vet.com/wp-content/uploads" in html  # Image included
    assert "Bibliographie" in html
