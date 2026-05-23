"""Pydantic models for verso-content-manager."""

from typing import Any, Literal

from pydantic import BaseModel, Field


class Block(BaseModel):
    """Base block model with type discrimination."""

    type: Literal[
        "hero",
        "text",
        "image",
        "two_columns",
        "three_columns",
        "list",
        "video",
        "cta",
        "quote",
    ]


class HeroBlock(Block):
    """Hero section block."""

    type: Literal["hero"] = "hero"
    text: str
    image_url: str | None = None


class TextBlock(Block):
    """Text block with optional heading."""

    type: Literal["text"] = "text"
    heading: str | None = None
    content: str  # HTML content


class ImageBlock(Block):
    """Image block."""

    type: Literal["image"] = "image"
    url: str
    alt: str
    caption: str | None = None


class TwoColumnsBlock(Block):
    """Two-column layout block."""

    type: Literal["two_columns"] = "two_columns"
    left: dict[str, Any]  # Nested block
    right: dict[str, Any]  # Nested block


class ThreeColumnsBlock(Block):
    """Three-column layout block."""

    type: Literal["three_columns"] = "three_columns"
    columns: list[dict[str, Any]]  # 3 nested blocks


class ListBlock(Block):
    """Unordered list block."""

    type: Literal["list"] = "list"
    items: list[str]


class VideoBlock(Block):
    """Video embed block (YouTube/Vimeo)."""

    type: Literal["video"] = "video"
    url: str


class CTABlock(Block):
    """Call-to-action button block."""

    type: Literal["cta"] = "cta"
    text: str
    url: str


class QuoteBlock(Block):
    """Quote/blockquote block."""

    type: Literal["quote"] = "quote"
    text: str
    author: str | None = None


class ArticleRequest(BaseModel):
    """Request model for creating/updating articles."""

    title: str = Field(..., min_length=5, max_length=200)
    excerpt: str | None = Field(None, max_length=160)
    slug: str | None = None
    status: Literal["draft", "publish", "pending"] = "draft"
    featured_image_url: str | None = None
    categories: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    seo_keywords: list[str] = Field(default_factory=list)
    blocks: list[dict[str, Any]] = Field(default_factory=list)


class ArticleResponse(BaseModel):
    """Response model for article operations."""

    id: int
    title: str
    status: str
    link: str
    date: str | None = None
    excerpt: str | None = None
    categories: list[int] = Field(default_factory=list)
    tags: list[int] = Field(default_factory=list)


class MediaUploadRequest(BaseModel):
    """Request model for uploading media."""

    url: str
    alt: str
    title: str | None = None


class MediaResponse(BaseModel):
    """Response model for media upload."""

    id: int
    wp_url: str
    filename: str
    size: int


# WrittenContent Models (article-writer integration)


class RedactionContext(BaseModel):
    """Redaction context for article generation."""

    objective: str
    target_audience: str
    word_count_target: int = 2000
    language: str = "fr"
    specific_instructions: str | None = None


class WrittenSection(BaseModel):
    """Section of written content."""

    id: str
    title: str
    content: str  # Markdown with [CITE:zotero_key] markers
    word_count: int
    references_used: list[str] = Field(default_factory=list)
    selected_images: list[str] = Field(default_factory=list)  # attachment_keys


class SelectedImage(BaseModel):
    """Selected image for article."""

    zotero_key: str
    attachment_key: str
    dropbox_url: str
    caption: str
    placement_section: str  # Target section ID


class BibliographyEntry(BaseModel):
    """Bibliography entry."""

    zotero_key: str
    formatted: str


class WrittenContentMetadata(BaseModel):
    """Metadata for written content."""

    total_words: int
    total_images: int
    profile_used: str
    generation_time_ms: float


class WrittenContent(BaseModel):
    """Complete written content from article-writer."""

    id: str
    package_id: str
    profile_name: str
    context: RedactionContext
    sections: list[WrittenSection]
    selected_images: list[SelectedImage]
    bibliography: list[BibliographyEntry]
    metadata: WrittenContentMetadata


class PublishRequest(BaseModel):
    """Request to publish WrittenContent to WordPress."""

    content: WrittenContent
    status: Literal["draft", "publish"] = "draft"
    preview_only: bool = False


class PublishResponse(BaseModel):
    """Response from content publishing."""

    post_id: int | None = None
    url: str | None = None
    status: str
    featured_image_url: str | None = None
    edit_url: str | None = None
    error_message: str | None = None
    preview_html: str | None = None
