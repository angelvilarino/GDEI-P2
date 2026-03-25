"""
Database/Orion connectivity detection and backend management.
Determines which backend (Orion or SQLite) should be used at startup.
"""
import os
import requests
import logging
from typing import Literal

logger = logging.getLogger(__name__)

# Global backend state
ACTIVE_BACKEND: Literal["orion", "sqlite"] = "sqlite"


def check_orion_connectivity(orion_url: str, timeout: int = 5) -> bool:
    """
    Check if Orion Context Broker is available.
    
    Args:
        orion_url (str): Base URL of Orion (e.g. "http://localhost:1026")
        timeout (int): Request timeout in seconds.
    
    Returns:
        bool: True if Orion is reachable and responds to version endpoint
              (or fallback entities endpoint).
    """
    base_url = (orion_url or '').rstrip('/')
    if not base_url:
        logger.warning(" [CONNECTIVITY] Orion URL is empty")
        return False

    try:
        response = requests.get(
            f"{base_url}/version",
            timeout=timeout
        )
        is_available = response.status_code == 200
        if is_available:
            logger.info(f" [CONNECTIVITY] Orion is available at {base_url} (GET /version)")
            return True
    except requests.RequestException:
        pass

    try:
        fallback_response = requests.get(
            f"{base_url}/v2/entities",
            params={'limit': 1, 'options': 'keyValues'},
            timeout=timeout,
        )
        is_available = fallback_response.status_code == 200
        if is_available:
            logger.info(f" [CONNECTIVITY] Orion is available at {base_url} (GET /v2/entities)")
        return is_available
    except requests.RequestException as e:
        logger.warning(f" [CONNECTIVITY] Orion unavailable at {base_url}: {e}")
        return False


def get_active_backend(orion_url: str | None = None, timeout: int | None = None) -> Literal["orion", "sqlite"]:
    """
    Determine and return the active backend at runtime.
    Attempts Orion first, falls back to SQLite if unavailable.
    
    Returns:
        str: Either 'orion' or 'sqlite'.
    """
    global ACTIVE_BACKEND
    
    # Try to connect to Orion (runtime-configurable values)
    if orion_url is None:
        orion_host = os.environ.get("ORION_HOST") or "localhost"
        orion_port = os.environ.get("ORION_PORT") or "1026"
        orion_url = os.environ.get("ORION_URL") or f"http://{orion_host}:{orion_port}"
    if timeout is None:
        timeout = int(os.environ.get("ORION_TIMEOUT") or 5)

    if check_orion_connectivity(orion_url, timeout):
        ACTIVE_BACKEND = "orion"
        logger.info(f" [BACKEND] Using Orion as active backend ({orion_url})")
    else:
        ACTIVE_BACKEND = "sqlite"
        logger.info(" [BACKEND] Using SQLite as fallback backend")
    
    return ACTIVE_BACKEND


def is_orion_active() -> bool:
    """
    Check if Orion is the currently active backend.
    
    Returns:
        bool: True if Orion is active, False if SQLite is active.
    """
    return ACTIVE_BACKEND == "orion"
