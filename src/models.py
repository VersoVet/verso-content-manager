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
