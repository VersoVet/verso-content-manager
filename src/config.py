"""Configuration for verso-content-manager skill."""

import os
from pathlib import Path

import yaml

# Load YAML config
_CONFIG_PATH = Path(__file__).parent.parent / "config" / "verso-content-manager.yaml"
with open(_CONFIG_PATH) as _f:
    CONFIG: dict = yaml.safe_load(_f)

# API Configuration
PORT: int = int(os.getenv("PORT", str(CONFIG["settings"]["port"])))
SERVICE_NAME: str = "verso-content-manager"
VERSION: str = "1.0.14"

# WordPress Configuration
WP_URL: str = CONFIG["endpoints"]["wordpress"]
WP_TIMEOUT: float = CONFIG["settings"]["wp_timeout"]

# Vault Configuration
VAULT_URL: str = os.getenv("VAULT_URL", CONFIG["endpoints"]["vault"])
VAULT_TOKEN: str = os.getenv("ONYX_VAULT_TOKEN", "")

# Skill Directories
SKILL_DIR: Path = Path(__file__).parent.parent
TEMPLATES_DIR: Path = SKILL_DIR / "templates"

# Image Optimization
IMAGE_MAX_WIDTH: int = CONFIG["images"]["max_width"]
IMAGE_MAX_HEIGHT: int = CONFIG["images"]["max_height"]
IMAGE_COLUMN_MAX_WIDTH: int = CONFIG["images"]["column_max_width"]
IMAGE_COLUMN_MAX_HEIGHT: int = CONFIG["images"]["column_max_height"]
WEBP_QUALITY: int = CONFIG["images"]["webp_quality"]
IMAGE_FORMAT: str = CONFIG["images"]["format"]

# Verso Vet Design Colors
COLOR_PRIMARY: str = CONFIG["design"]["color_primary"]
COLOR_ACCENT: str = CONFIG["design"]["color_accent"]
