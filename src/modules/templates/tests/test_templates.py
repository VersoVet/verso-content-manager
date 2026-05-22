"""Tests for templates module."""

import pytest


def test_get_template_list() -> None:
    """Test listing available templates."""
    from src.modules.templates.service import get_available_templates

    templates = get_available_templates()
    assert isinstance(templates, list)
    assert len(templates) > 0
    assert "presse" in templates


def test_load_template() -> None:
    """Test loading a specific template."""
    from src.modules.templates.service import get_template

    template = get_template("presse")
    assert isinstance(template, dict)
    assert "title" in template or "_template" in template


def test_load_template_invalid() -> None:
    """Test loading invalid template.

    Raises:
        ValueError: If template not found.
    """
    from src.modules.templates.service import get_template

    with pytest.raises((FileNotFoundError, ValueError)):
        get_template("nonexistent_template")


def test_template_structure() -> None:
    """Test that templates have correct structure."""
    from src.modules.templates.service import get_available_templates, get_template

    templates = get_available_templates()
    for template_name in templates[:1]:  # Test at least one
        template = get_template(template_name)
        assert isinstance(template, dict)
        assert "title" in template or "_template" in template
