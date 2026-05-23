"""Dropbox image download module."""

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


async def get_secret(key: str) -> str:
    """Retrieve secret from OnyxVault.

    Args:
        key: Secret key name.

    Returns:
        Secret value.

    Raises:
        Exception: If Vault is unreachable.
    """
    import os

    token = os.getenv("ONYX_VAULT_TOKEN", "")
    if not token:
        raise ValueError("ONYX_VAULT_TOKEN not set")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://10.0.0.44:8050/vault/{key}",
            headers={"X-Vault-Token": token},
            timeout=10.0,
        )
        response.raise_for_status()
        return response.json().get("value", "")


async def download_dropbox_image(dropbox_url: str) -> bytes:
    """Download image from Dropbox URL.

    Tries Dropbox API first, falls back to direct URL with dl=1.

    Args:
        dropbox_url: Dropbox sharing URL.

    Returns:
        Image bytes.

    Raises:
        Exception: If download fails.
    """
    # Try Dropbox API first
    try:
        token = await get_secret("dropbox_token")
        headers: dict[str, Any] = {"Authorization": f"Bearer {token}"}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://content.dropboxapi.com/2/sharing/get_shared_link_file",
                headers=headers
                | {"Dropbox-API-Arg": f'{{"url": "{dropbox_url}"}}'},
                timeout=30.0,
            )
            response.raise_for_status()
            logger.info(f"Downloaded image via Dropbox API: {len(response.content)} bytes")
            return response.content
    except Exception as e:
        logger.warning(f"Dropbox API failed, trying fallback: {e}")

    # Fallback: direct URL with dl=1
    try:
        direct_url = dropbox_url.replace("dl=0", "dl=1")
        if "dl=" not in direct_url:
            sep = "&" if "?" in direct_url else "?"
            direct_url += f"{sep}dl=1"

        async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
            response = await client.get(direct_url)
            response.raise_for_status()
            logger.info(f"Downloaded image via fallback URL: {len(response.content)} bytes")
            return response.content
    except Exception as e:
        logger.error(f"Dropbox image download failed: {e}")
        raise ValueError(f"Failed to download Dropbox image: {e}")
