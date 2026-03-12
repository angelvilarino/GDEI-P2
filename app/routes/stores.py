"""
Stores: web views (placeholder) + REST API endpoints.
"""
from flask import Blueprint, jsonify, request, abort, current_app
from app.services import entity_service

stores_bp = Blueprint('stores', __name__)


# ---------------------------------------------------------------------------
# Views (text placeholder — HTML templates to be added in Issue #4)
# ---------------------------------------------------------------------------

@stores_bp.route('/stores')
def stores_list():
    return "STORES LIST — template pending (Issue #4)", 200


@stores_bp.route('/stores/<store_id>')
def store_detail(store_id):
    return f"STORE DETAIL [{store_id}] — template pending (Issue #4)", 200


# ---------------------------------------------------------------------------
# API — list + create
# ---------------------------------------------------------------------------

@stores_bp.route('/api/stores', methods=['GET'])
def api_stores_list():
    return jsonify(entity_service.get_stores())


@stores_bp.route('/api/stores', methods=['POST'])
def api_stores_create():
    data = request.get_json(silent=True)
    if not data:
        abort(400, description="JSON request body required")
    try:
        store = entity_service.create_store(data)
        return jsonify(store), 201
    except ValueError as e:
        abort(400, description=str(e))
    except Exception as e:
        current_app.logger.error(f"create_store: {e}")
        abort(500)


# ---------------------------------------------------------------------------
# API — detail + update + delete
# ---------------------------------------------------------------------------

@stores_bp.route('/api/stores/<store_id>', methods=['GET'])
def api_store_detail(store_id):
    store = entity_service.get_store(store_id)
    if store is None:
        abort(404, description=f"Store '{store_id}' not found")
    return jsonify(store)


@stores_bp.route('/api/stores/<store_id>', methods=['PUT'])
def api_store_update(store_id):
    data = request.get_json(silent=True)
    if not data:
        abort(400, description="JSON request body required")
    try:
        store = entity_service.update_store(store_id, data)
        if store is None:
            abort(404, description=f"Store '{store_id}' not found")
        return jsonify(store)
    except ValueError as e:
        abort(400, description=str(e))
    except Exception as e:
        current_app.logger.error(f"update_store: {e}")
        abort(500)


@stores_bp.route('/api/stores/<store_id>', methods=['DELETE'])
def api_store_delete(store_id):
    if not entity_service.delete_store(store_id):
        abort(404, description=f"Store '{store_id}' not found")
    return jsonify({"message": f"Store '{store_id}' deleted"})
