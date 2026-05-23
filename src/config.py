"""Configuration for verso-content-manager skill."""

import os
from pathlib import Path

# API Configuration
PORT: int = int(os.getenv("PORT", "8091"))
SERVICE_NAME: str = "verso-content-manager"
VERSION: str = "1.0.8"

# WordPress Configuration
WP_URL: str = "https://verso-vet.com/wp-json"
WP_TIMEOUT: float = 20.0

# Vault Configuration
VAULT_URL: str = os.getenv("VAULT_URL", "http://10.0.0.44:8050/vault")
VAULT_TOKEN: str = os.getenv("ONYX_VAULT_TOKEN", "")

# Skill Directories
SKILL_DIR: Path = Path(__file__).parent.parent
TEMPLATES_DIR: Path = SKILL_DIR / "templates"

# Image Optimization
IMAGE_MAX_WIDTH: int = 1200
IMAGE_MAX_HEIGHT: int = 1200
IMAGE_COLUMN_MAX_WIDTH: int = 600
IMAGE_COLUMN_MAX_HEIGHT: int = 400
WEBP_QUALITY: int = 85
IMAGE_FORMAT: str = "WebP"

# Verso Vet Design Colors
COLOR_PRIMARY: str = "#1c2445"
COLOR_ACCENT: str = "#e74c3c"
