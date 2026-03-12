"""
Database/Orion connectivity detection and backend management.
Determines which backend (Orion or SQLite) should be used at startup.
"""
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
        bool: True if Orion is reachable and responds to version endpoint.
    """
    try:
        response = requests.get(
            f"{orion_url}/version",
            timeout=timeout
        )
        is_available = response.status_code == 200
        if is_available:
            logger.info(f" [CONNECTIVITY] Orion is available at {orion_url}")
        return is_available
    except requests.RequestException as e:
        logger.warning(f" [CONNECTIVITY] Orion unavailable at {orion_url}: {e}")
        return False


def get_active_backend() -> Literal["orion", "sqlite"]:
    """
    Determine and return the active backend at runtime.
    Attempts Orion first, falls back to SQLite if unavailable.
    
    Returns:
        str: Either 'orion' or 'sqlite'.
    """
    global ACTIVE_BACKEND
    
    # Try to connect to Orion
    from config import DevelopmentConfig
    if check_orion_connectivity(DevelopmentConfig.ORION_URL, DevelopmentConfig.ORION_TIMEOUT):
        ACTIVE_BACKEND = "orion"
        logger.info(" [BACKEND] Using Orion as active backend")
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
