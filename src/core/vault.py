"""Vault client for retrieving secrets."""

import json
import logging
from typing import Any, cast

import httpx

from src.config import VAULT_TOKEN, VAULT_URL

logger = logging.getLogger(__name__)

# Cache with 5-minute TTL
_cache: dict[str, tuple[float, Any]] = {}
CACHE_TTL: float = 300.0  # 5 minutes


async def get_secret(key: str) -> str:
    """Retrieve a secret from Vault.

    Args:
        key: Secret key name.

    Returns:
        Secret value as string.

    Raises:
        ValueError: If secret not found or Vault request fails.
    """
    import time

    # Check cache
    if key in _cache:
        cached_time, cached_value = _cache[key]
        if time.time() - cached_time < CACHE_TTL:
            logger.debug(f"Cache hit for secret: {key}")
            return cast(str, cached_value)

    # Fetch from Vault
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"{VAULT_URL}/{key}",
            headers={"X-Vault-Token": VAULT_TOKEN},
        )
        resp.raise_for_status()
        value: str = resp.json()["value"]

    # Cache result
    import time

    _cache[key] = (time.time(), value)
    logger.info(f"Retrieved secret: {key}")
    return value


async def get_secret_json(key: str) -> dict[str, Any]:
    """Retrieve a secret and parse as JSON.

    Args:
        key: Secret key name.

    Returns:
        Parsed JSON dictionary.
    """
    raw = await get_secret(key)
    if raw.startswith("{"):
        return json.loads(raw)  # type: ignore[no-any-return]
    return {"value": raw}
