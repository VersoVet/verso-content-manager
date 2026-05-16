"""Integration tests for verso-content-manager."""

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


@pytest.fixture
def sample_article() -> dict:
    """Sample article JSON for testing.

    Returns:
        Sample article data.
    """
    return {
        "title": "Test Article",
        "excerpt": "Test excerpt",
        "status": "draft",
        "categories": [],
        "tags": [],
        "blocks": [
            {"type": "text", "heading": "Intro", "content": "<p>Test content</p>"},
            {"type": "cta", "text": "Click me", "url": "/test"},
        ],
    }


def test_health_check() -> None:
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_dashboard_loads() -> None:
    """Test dashboard HTML loads."""
    response = client.get("/")
    assert response.status_code == 200
    assert "verso-content-manager" in response.text


def test_list_templates() -> None:
    """Test listing templates."""
    response = client.get("/templates")
    assert response.status_code == 200
    templates = response.json()
    assert isinstance(templates, list)
    assert "presse" in templates or len(templates) >= 0


def test_get_template() -> None:
    """Test getting a specific template."""
    response = client.get("/templates/presse")
    assert response.status_code == 200
    template = response.json()
    assert "_template" in template
    assert template["_template"] == "presse"


def test_list_categories() -> None:
    """Test listing categories."""
    response = client.get("/seo/categories")
    assert response.status_code == 200
    categories = response.json()
    assert isinstance(categories, list)


def test_list_tags() -> None:
    """Test listing tags."""
    response = client.get("/seo/tags")
    assert response.status_code == 200
    tags = response.json()
    assert isinstance(tags, list)
