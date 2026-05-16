# verso-content-manager API Documentation

## Overview

verso-content-manager is a FastAPI-based skill for managing WordPress articles at verso-vet.com through JSON block-based content structures. It converts block-structured content to WordPress REST API calls.

## Base URL

```
http://10.0.0.44:8091
```

## Health & Status

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "verso-content-manager",
  "version": "1.0.0"
}
```

### GET /

Interactive dashboard for managing articles.

**Response:** HTML dashboard with:
- Article creation form with template selection
- Articles list with filtering
- Quick publish/delete actions

---

## Articles Management

### POST /articles

Create a new article from JSON blocks.

**Request:**
```json
{
  "title": "Article Title",
  "excerpt": "Short excerpt (~160 chars)",
  "slug": "article-slug",
  "status": "draft",
  "categories": ["Category 1"],
  "tags": ["tag1", "tag2"],
  "seo_keywords": ["keyword1"],
  "blocks": [
    {"type": "hero", "text": "Welcome", "image_url": null},
    {"type": "text", "heading": "Section 1", "content": "<p>Content</p>"},
    {"type": "cta", "text": "Click", "url": "/action"}
  ]
}
```

**Response:**
```json
{
  "id": 1234,
  "title": "Article Title",
  "status": "draft",
  "link": "https://verso-vet.com/?p=1234",
  "date": "2025-02-15T10:30:00",
  "excerpt": "Short excerpt",
  "categories": [5],
  "tags": [12, 15]
}
```

**Status Codes:**
- `200`: Article created successfully
- `500`: Server error

---

### GET /articles

List articles with optional filtering.

**Query Parameters:**
- `status` (string, default: "publish"): Filter by status (draft, publish, pending)
- `limit` (integer, default: 10): Maximum number of articles to return
- `search` (string): Search keyword in title/content

**Example:**
```
GET /articles?status=draft&limit=20&search=vet
```

**Response:**
```json
[
  {
    "id": 1234,
    "title": "Article Title",
    "status": "draft",
    "date": "2025-02-15T10:30:00",
    "link": "https://verso-vet.com/?p=1234"
  }
]
```

---

### GET /articles/{post_id}

Retrieve a single article by ID.

**Path Parameters:**
- `post_id` (integer): WordPress post ID

**Response:**
```json
{
  "id": 1234,
  "title": "Article Title",
  "status": "draft",
  "link": "https://verso-vet.com/?p=1234",
  "date": "2025-02-15T10:30:00",
  "excerpt": "Short excerpt",
  "categories": [5],
  "tags": [12, 15]
}
```

---

### PATCH /articles/{post_id}

Update an existing article.

**Path Parameters:**
- `post_id` (integer): WordPress post ID

**Request (partial update):**
```json
{
  "title": "Updated Title",
  "status": "publish",
  "blocks": [
    {"type": "text", "heading": "New content", "content": "<p>Updated</p>"}
  ]
}
```

**Response:**
```json
{
  "id": 1234,
  "title": "Updated Title",
  "status": "publish",
  "link": "https://verso-vet.com/?p=1234"
}
```

---

### DELETE /articles/{post_id}

Delete an article.

**Path Parameters:**
- `post_id` (integer): WordPress post ID

**Response:**
```json
{
  "message": "Article 1234 deleted"
}
```

---

### POST /articles/{post_id}/publish

Publish a draft article.

**Path Parameters:**
- `post_id` (integer): WordPress post ID

**Response:**
```json
{
  "id": 1234,
  "title": "Article Title",
  "status": "publish",
  "link": "https://verso-vet.com/?p=1234"
}
```

---

## Media Management

### POST /media/upload

Upload media from external URL to WordPress library with automatic optimization.

**Request:**
```json
{
  "url": "https://example.com/image.jpg",
  "alt": "Image description",
  "title": "Image Title"
}
```

**Response:**
```json
{
  "id": 567,
  "wp_url": "https://verso-vet.com/wp-content/uploads/2025/02/image.webp",
  "filename": "image.webp",
  "size": 45230
}
```

**Features:**
- Automatic image optimization
- Conversion to WebP format
- Responsive resizing based on context
- Integration with WordPress media library

---

## SEO & Taxonomy

### GET /seo/categories

List all categories.

**Response:**
```json
[
  {
    "id": 5,
    "name": "Santé Animale",
    "slug": "sante-animale"
  }
]
```

---

### POST /seo/categories

Create a new category.

**Query Parameters:**
- `name` (string, required): Category name
- `slug` (string, optional): Category slug

**Response:**
```json
{
  "id": 15,
  "name": "New Category",
  "slug": "new-category"
}
```

---

### GET /seo/tags

List all tags.

**Response:**
```json
[
  {
    "id": 12,
    "name": "santé",
    "slug": "sante"
  }
]
```

---

### POST /seo/tags

Create a new tag.

**Query Parameters:**
- `name` (string, required): Tag name
- `slug` (string, optional): Tag slug

**Response:**
```json
{
  "id": 35,
  "name": "new-tag",
  "slug": "new-tag"
}
```

---

## Templates

### GET /templates

List available article templates.

**Response:**
```json
[
  "presse",
  "pathologie",
  "outil"
]
```

---

### GET /templates/{name}

Get a template by name.

**Path Parameters:**
- `name` (string): Template name (presse, pathologie, outil)

**Response:**
```json
{
  "_template": "presse",
  "_description": "Article de presse / actualité",
  "title": "[TITRE DE L'ARTICLE]",
  "excerpt": "[Résumé accrocheur]",
  "status": "draft",
  "categories": ["Actualités"],
  "tags": [],
  "blocks": [
    {"type": "text", "heading": "[Chapô]", "content": "<p>[Intro]</p>"},
    {"type": "image", "url": "[URL_IMAGE]", "alt": "[Description]"}
  ]
}
```

---

## Block Types

Supported content blocks for articles:

| Type | Description | Fields |
|------|-------------|--------|
| `hero` | Full-width hero section | text, image_url |
| `text` | Paragraph with optional heading | heading, content |
| `image` | Centered image | url, alt, caption |
| `two_columns` | Two-column layout | left, right (nested blocks) |
| `three_columns` | Three-column layout | columns (array of blocks) |
| `list` | Unordered list | items (array of strings) |
| `video` | Video embed (YouTube/Vimeo) | url |
| `cta` | Call-to-action button | text, url |
| `quote` | Blockquote | text, author |

---

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200`: Success
- `400`: Bad request (invalid JSON)
- `404`: Resource not found
- `500`: Server error

Error responses include detail:
```json
{
  "detail": "Failed to create article: ..."
}
```

---

## Examples

### Create and publish an article

```bash
# 1. Create draft article
curl -X POST http://10.0.0.44:8091/articles \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Santé du Chat",
    "excerpt": "5 conseils pour maintenir votre chat en bonne santé",
    "status": "draft",
    "categories": ["Santé Animale"],
    "blocks": [
      {"type": "hero", "text": "Introduction"},
      {"type": "text", "heading": "Conseil 1", "content": "<p>Contenu...</p>"},
      {"type": "cta", "text": "Consulter", "url": "/consultation/"}
    ]
  }'

# Response includes: {"id": 1234, ...}

# 2. Publish the article
curl -X POST http://10.0.0.44:8091/articles/1234/publish
```

### Upload and use an image

```bash
# Upload image from external URL
curl -X POST http://10.0.0.44:8091/media/upload \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/cat.jpg",
    "alt": "Chat en bonne santé"
  }'

# Response: {"id": 567, "wp_url": "https://verso-vet.com/wp-content/uploads/.../cat.webp"}

# Use the wp_url in article blocks
```

---

## Dashboard

Interactive web dashboard available at `http://10.0.0.44:8091/`

**Features:**
- Create articles from templates or custom JSON
- Upload JSON files
- View all articles with status filtering
- Publish draft articles
- Delete articles
- Live preview with syntax highlighting
