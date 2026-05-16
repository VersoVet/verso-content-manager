"""Template management service."""

import json
import logging
from pathlib import Path
from typing import Any

from src.config import TEMPLATES_DIR

logger = logging.getLogger(__name__)


def get_available_templates() -> list[str]:
    """List available template names.

    Returns:
        List of template names (without .json extension).
    """
    try:
        templates_path = Path(TEMPLATES_DIR)
        if not templates_path.exists():
            logger.warning(f"Templates directory not found: {TEMPLATES_DIR}")
            return []

        template_files = list(templates_path.glob("*.json"))
        return [f.stem for f in template_files]
    except Exception as e:
        logger.error(f"Failed to list templates: {str(e)}")
        return []


def get_template(name: str) -> dict[str, Any]:
    """Load a template by name.

    Args:
        name: Template name (without .json extension).

    Returns:
        Template data as dictionary.

    Raises:
        ValueError: If template not found or loading fails.
    """
    try:
        template_path = Path(TEMPLATES_DIR) / f"{name}.json"

        if not template_path.exists():
            raise ValueError(f"Template not found: {name}")

        with open(template_path, encoding="utf-8") as f:
            template: dict[str, Any] = json.load(f)

        logger.info(f"Loaded template: {name}")
        return template
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse template {name}: {str(e)}")
        raise ValueError(f"Invalid template JSON: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to load template {name}: {str(e)}")
        raise ValueError(f"Failed to load template: {str(e)}")
