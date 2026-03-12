"""
NGSIv2 HTTP client for FIWARE Orion Context Broker.
All read operations use ?options=keyValues for a flat response.
Writes use full NGSIv2 attribute format for type safety.
"""
import requests
from flask import current_app

_HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
}


def _base_url():
    return current_app.config.get('ORION_URL', 'http://localhost:1026')


def _timeout():
    return current_app.config.get('ORION_TIMEOUT', 5)


def get_entities(entity_type, limit=100, offset=0, extra_params=None):
    """GET /v2/entities?type=<type>&options=keyValues
    Returns a list of flat dicts (keyValues representation).
    """
    params = {
        'type': entity_type,
        'limit': limit,
        'offset': offset,
        'options': 'keyValues',
    }
    if extra_params:
        params.update(extra_params)
    r = requests.get(
        f"{_base_url()}/v2/entities",
        headers=_HEADERS,
        params=params,
        timeout=_timeout(),
    )
    r.raise_for_status()
    return r.json()


def get_entity(entity_id):
    """GET /v2/entities/<id>?options=keyValues
    Returns flat dict or None on 404.
    """
    r = requests.get(
        f"{_base_url()}/v2/entities/{entity_id}",
        headers=_HEADERS,
        params={'options': 'keyValues'},
        timeout=_timeout(),
    )
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.json()


def create_entity(payload):
    """POST /v2/entities (full NGSIv2 attribute format).
    Raises on error. Returns the entity id.
    """
    r = requests.post(
        f"{_base_url()}/v2/entities",
        headers=_HEADERS,
        json=payload,
        timeout=_timeout(),
    )
    r.raise_for_status()
    return payload.get('id')


def update_entity_attrs(entity_id, attrs):
    """PATCH /v2/entities/<id>/attrs (full NGSIv2 attrs format).
    Returns False on 404, True on success.
    """
    r = requests.patch(
        f"{_base_url()}/v2/entities/{entity_id}/attrs",
        headers=_HEADERS,
        json=attrs,
        timeout=_timeout(),
    )
    if r.status_code == 404:
        return False
    r.raise_for_status()
    return True


def delete_entity(entity_id):
    """DELETE /v2/entities/<id>.
    Returns False on 404, True on success.
    """
    r = requests.delete(
        f"{_base_url()}/v2/entities/{entity_id}",
        headers=_HEADERS,
        timeout=_timeout(),
    )
    if r.status_code == 404:
        return False
    r.raise_for_status()
    return True
