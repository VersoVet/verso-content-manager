"""WordPress REST API client with proper authentication handling."""

import logging
from typing import Any

import httpx

from src.config import WP_TIMEOUT, WP_URL
from src.core.vault import get_secret_json

logger = logging.getLogger(__name__)


async def _get_auth() -> tuple[str, str]:
    """Retrieve WordPress authentication credentials from Vault.

    Returns:
        Tuple of (username, app_password).
    """
    creds = await get_secret_json("wordpress_credentials")
    return creds["username"], creds["app_password"]


async def wp_get(path: str, params: dict[str, Any] | None = None) -> dict[str, Any] | list[Any]:
    """GET request to WordPress REST API.

    Uses --http1.1 + Pragma headers to work around Cloudflare caching issues.

    Args:
        path: API endpoint path (e.g., "/wp/v2/posts").
        params: Optional query parameters.

    Returns:
        JSON response from WordPress.
    """
    username, app_password = await _get_auth()

    async with httpx.AsyncClient(http1=True, http2=False, timeout=WP_TIMEOUT) as client:
        resp = await client.get(
            f"{WP_URL}{path}",
            auth=(username, app_password),
            params=params,
            headers={
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
            },
        )
        resp.raise_for_status()
        return resp.json()  # type: ignore[no-any-return]


async def wp_post(
    path: str, data: dict[str, Any] | None = None, json_data: dict[str, Any] | None = None
) -> dict[str, Any]:
    """POST request to WordPress REST API.

    Args:
        path: API endpoint path.
        data: Form data (for file uploads).
        json_data: JSON body data.

    Returns:
        JSON response from WordPress.
    """
    username, app_password = await _get_auth()

    async with httpx.AsyncClient(http1=True, http2=False, timeout=WP_TIMEOUT) as client:
        resp = await client.post(
            f"{WP_URL}{path}",
            auth=(username, app_password),
            data=data,
            json=json_data,
            headers={
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
            },
        )
        resp.raise_for_status()
        return resp.json()  # type: ignore[no-any-return]


async def wp_patch(path: str, json_data: dict[str, Any]) -> dict[str, Any]:
    """PATCH request to WordPress REST API.

    Args:
        path: API endpoint path.
        json_data: JSON body data.

    Returns:
        JSON response from WordPress.
    """
    username, app_password = await _get_auth()

    async with httpx.AsyncClient(http1=True, http2=False, timeout=WP_TIMEOUT) as client:
        resp = await client.patch(
            f"{WP_URL}{path}",
            auth=(username, app_password),
            json=json_data,
            headers={
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
            },
        )
        resp.raise_for_status()
        return resp.json()  # type: ignore[no-any-return]


async def wp_delete(path: str) -> dict[str, Any]:
    """DELETE request to WordPress REST API.

    Args:
        path: API endpoint path.

    Returns:
        JSON response from WordPress.
    """
    username, app_password = await _get_auth()

    async with httpx.AsyncClient(http1=True, http2=False, timeout=WP_TIMEOUT) as client:
        resp = await client.delete(
            f"{WP_URL}{path}",
            auth=(username, app_password),
            headers={
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
            },
        )
        resp.raise_for_status()
        return resp.json()  # type: ignore[no-any-return]
