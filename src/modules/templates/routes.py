"""FastAPI routes for template management."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from src.modules.templates.service import get_available_templates, get_template

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("", response_model=list[str])
async def list_templates_endpoint() -> list[str]:
    """List available templates.

    Returns:
        List of template names.
    """
    try:
        templates = get_available_templates()
        return templates
    except Exception as e:
        logger.error(f"Failed to list templates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{name}", response_model=dict[str, Any])
async def get_template_endpoint(name: str) -> dict[str, Any]:
    """Get a specific template by name.

    Args:
        name: Template name (without .json extension).

    Returns:
        Template data.
    """
    try:
        template = get_template(name)
        return template
    except ValueError as e:
        logger.error(f"Template not found: {name}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get template {name}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
