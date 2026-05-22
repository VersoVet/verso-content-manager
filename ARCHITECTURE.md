# verso-content-manager Architecture

## 🚀 Status: PRODUCTION READY

**Deployment Status**: ✅ **LIVE on AXON (10.0.0.21)**
- Validation: ✅ PASSED (0 errors, 3 optional warnings)
- Health Check: ✅ OPERATIONAL
- API Endpoints: ✅ ALL FUNCTIONAL
- WordPress Integration: ✅ CONNECTED
- Last Updated: 2026-05-22 13:29:12 UTC

---

## Overview

verso-content-manager is a FastAPI-based Forge skill that automates WordPress article management at verso-vet.com. It provides:

- **JSON block-based content** conversion to WordPress REST API calls
- **Image optimization** and WebP conversion before upload
- **Template system** for predefined article structures
- **Interactive dashboard** for non-technical users
- **SEO management** (categories, tags, slugs)

## Technology Stack

- **Framework**: FastAPI (Python 3.12+)
- **HTTP Client**: httpx (async)
- **Validation**: Pydantic
- **Image Processing**: Pillow
- **Server**: Uvicorn
- **Infrastructure**: Forge Skill (OnyxSoma 10.0.0.44, port 8091)

## Project Structure

```
verso-content-manager/
├── manifest.json                 # Skill configuration
├── requirements.txt              # Python dependencies
├── .gitignore                    # Git ignore patterns
├── API.md                        # API documentation
├── ARCHITECTURE.md               # This file
├── TODO.md                       # Task tracking
│
├── templates/                    # Article templates
│   ├── presse.json              # Press article template
│   ├── pathologie.json          # Animal pathology template
│   └── outil.json               # Equipment article template
│
├── src/
│   ├── __init__.py
│   ├── config.py                # Configuration constants
│   ├── models.py                # Pydantic models & types
│   ├── main.py                  # FastAPI app & dashboard
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── vault.py             # OnyxVault secret management
│   │   └── wp_client.py         # WordPress REST API client
│   │
│   └── modules/
│       ├── articles/            # Article CRUD operations
│       │   ├── __init__.py
│       │   ├── builder.py       # JSON blocks → HTML conversion
│       │   ├── service.py       # WordPress API service
│       │   ├── routes.py        # FastAPI routes
│       │   └── tests/
│       │       └── test_articles.py
│       │
│       ├── media/               # Image upload & optimization
│       │   ├── __init__.py
│       │   ├── optimizer.py     # Pillow image processing
│       │   ├── uploader.py      # WordPress media upload
│       │   ├── routes.py        # FastAPI routes
│       │   └── tests/
│       │       └── test_media.py
│       │
│       ├── seo/                 # SEO & taxonomy
│       │   ├── __init__.py
│       │   ├── service.py       # Category/tag management
│       │   ├── routes.py        # FastAPI routes
│       │   └── tests/
│       │       └── test_seo.py
│       │
│       └── templates/           # Template service
│           ├── __init__.py
│           ├── service.py       # Template file loading
│           ├── routes.py        # FastAPI routes
│           └── tests/
│               └── test_templates.py
│
└── tests/
    ├── __init__.py
    ├── test_integration.py      # End-to-end tests
    └── conftest.py              # pytest fixtures
```

## Core Components

### 1. Configuration (src/config.py)

Centralized configuration for:
- Port, URLs, and service name
- WordPress API endpoints
- Vault secret paths
- Image optimization settings
- Color definitions for HTML styling

### 2. Vault Integration (src/core/vault.py)

- Retrieves WordPress credentials from OnyxVault
- 5-minute TTL caching to minimize API calls
- Async implementation for non-blocking operations

### 3. WordPress REST API Client (src/core/wp_client.py)

Low-level HTTP client for WordPress REST API:
- Basic authentication using app_password
- HTTP/1.1 protocol (workaround for Cloudflare interference)
- Pragma headers to bypass caching issues
- Functions: `wp_get()`, `wp_post()`, `wp_patch()`, `wp_delete()`

### 4. Pydantic Models (src/models.py)

Type-safe request/response models:
- **Block Types**: Hero, Text, Image, TwoColumns, ThreeColumns, List, Video, CTA, Quote
- **ArticleRequest**: Input validation for article creation/update
- **ArticleResponse**: Standardized article response
- **MediaUploadRequest/Response**: Media management types

### 5. Article Builder (src/modules/articles/builder.py)

Converts JSON block structures to styled HTML:
- 9 block type handlers
- Inline CSS with Verso Vet branding (#1c2445 primary, #e74c3c accent)
- Responsive grid layouts
- Video embed extraction (YouTube/Vimeo)

### 6. Article Service (src/modules/articles/service.py)

WordPress article operations:
- `create_article()`: New article with blocks, categories, tags
- `update_article()`: Partial or full article updates
- `delete_article()`: Delete with force flag
- `publish_article()`: Status change to published
- `get_article()`: Retrieve single article
- `list_articles()`: List with filtering and search
- Helper functions for category/tag name-to-ID mapping

### 7. Media Service (src/modules/media/service.py)

Orchestrates media pipeline: download → optimize → upload.
- `create_media_from_url()`: Full pipeline for external URLs
- Combines optimizer + uploader into single service layer

### 8. Media Optimizer (src/modules/media/optimizer.py)

Image processing pipeline:
- HTTP download from external URLs
- Automatic format conversion to WebP
- Responsive resizing based on context (featured: 1200x630, article: 1000x600, column: 600x400)
- Quality optimization (WEBP_QUALITY = 85)

### 9. Media Uploader (src/modules/media/uploader.py)

WordPress media library integration:
- Upload optimized images to `/wp/v2/media`
- Set alt text and title metadata
- Return WordPress media URLs
- Wrapper for optimizer + upload pipeline

### 10. SEO Service (src/modules/seo/service.py)

Taxonomy management:
- Fetch categories and tags
- Create new categories with optional slugs
- Create new tags with optional slugs
- Category/tag name-to-ID conversion utilities

### 11. Template Service (src/modules/templates/service.py)

Template file management:
- Load JSON templates from `/templates/` directory
- List available templates
- JSON validation and error handling

### 12. FastAPI Application (src/main.py)

- Main app initialization with lifespan management
- Dashboard HTML with interactive UI
- Route inclusion for all modules
- Health check endpoint
- Logging configuration

## Data Flow

### Article Creation Flow

```
Client JSON
    ↓
[FastAPI Request Validation]
    ↓
[Article Builder: blocks → HTML]
    ↓
[WordPress Service: Create Post]
    ↓
[WordPress REST API]
    ↓
ArticleResponse (ID, link, status)
```

### Image Upload Flow

```
External URL
    ↓
[Media Optimizer: Download]
    ↓
[Pillow: Resize & Convert to WebP]
    ↓
[Media Uploader: POST to /wp/v2/media]
    ↓
[WordPress REST API]
    ↓
MediaResponse (WordPress URL)
```

## Security Considerations

### Authentication
- WordPress app_password retrieved from OnyxVault (never hardcoded)
- HTTP/1.1 + Pragma headers to bypass Cloudflare filtering
- Basic Auth used for REST API authentication

### Input Validation
- All inputs validated via Pydantic models
- File paths handled safely (no path traversal)
- HTML content from blocks passed directly to WordPress (trusted source)

### Error Handling
- Exceptions caught and logged at service level
- User-friendly error messages returned
- No sensitive information in error responses

## Performance Optimizations

1. **Vault Caching**: 5-minute TTL for credentials reduces API calls
2. **Async Operations**: All I/O operations are async (httpx, FastAPI)
3. **Image Optimization**: WebP conversion reduces file sizes (typically 30-50% smaller)
4. **HTTP/1.1**: Avoids HTTP/2 issues with Cloudflare
5. **Batch Operations**: Category/tag lookups batch 100 items per request

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | ≥0.100.0 | Web framework |
| uvicorn | ≥0.24.0 | ASGI server |
| httpx | ≥0.25.0 | Async HTTP client |
| pydantic | ≥2.0.0 | Data validation |
| Pillow | ≥10.0.0 | Image optimization |
| python-multipart | ≥0.0.6 | Form data parsing |
| onyx-sdk | ≥0.1.0 | Forge integration |

## Testing Strategy

### Unit Tests
- Block builder tests (each block type)
- Service function tests (mocked WordPress API)
- Model validation tests

### Integration Tests
- End-to-end dashboard tests
- API endpoint tests
- Error handling tests

### Manual Testing Checklist
1. Create article from template
2. Upload custom JSON
3. Publish draft article
4. Upload and use images
5. Manage categories/tags
6. List and filter articles

## Deployment

### Forge Configuration
- **Port**: 8091
- **Target**: OnyxAxon (10.0.0.21) 🚀 **PRODUCTION**
- **Type**: Python/FastAPI
- **Secret**: wordpress_credentials (Vault: 10.0.0.44:8050)
- **Status**: ✅ **DEPLOYED & LIVE**
- **Version**: 1.0.6
- **PID**: 2640927
- **Systemd**: onyx-verso-content-manager (active)

### Health Check
- Endpoint: `GET http://10.0.0.21:8091/health`
- Status: ✅ **HEALTHY**
- Returns: `{"status": "healthy", "service": "verso-content-manager", "version": "1.0.0"}`

### Dashboard
- Endpoint: `GET http://10.0.0.21:8091/`
- Interactive web UI for article management
- Status: ✅ **OPERATIONAL**

### API Documentation
- Swagger UI: `http://10.0.0.21:8091/docs`
- ReDoc: `http://10.0.0.21:8091/redoc`

### Repository
- GitHub: `https://github.com/VersoVet/verso-content-manager`
- Branch: `main` (production), `dev` (development)
- Last deployment: 2026-05-22 13:29:12 UTC

## Future Enhancements

1. **Article Scheduling**: Schedule publication for future dates
2. **Media Library Sync**: Browse WordPress media in dashboard
3. **Featured Image Auto-assignment**: Automatically set first image as featured
4. **Bulk Operations**: Create multiple articles from CSV/JSON
5. **Version History**: Track article revisions
6. **Slack Integration**: Publish notifications to Slack
7. **Preview Mode**: Live preview before publishing
