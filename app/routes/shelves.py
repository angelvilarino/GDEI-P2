"""
Shelves REST API endpoints.
Supports GET /api/shelves?store=<id>&excludeProduct=<id> for dynamic UI selectors.
"""
from flask import Blueprint, jsonify, request, abort, current_app
from app.services import entity_service

shelves_bp = Blueprint('shelves', __name__)


# ---------------------------------------------------------------------------
# API — list + create
# GET /api/shelves?store=<store_id>&excludeProduct=<product_id>
#     → shelves of that store that do NOT contain the given product
# ---------------------------------------------------------------------------

@shelves_bp.route('/api/shelves', methods=['GET'])
def api_shelves_list():
    store_id = request.args.get('store')
    exclude_product = request.args.get('excludeProduct')
    return jsonify(entity_service.get_shelves(store_id=store_id, exclude_product_id=exclude_product))


@shelves_bp.route('/api/shelves', methods=['POST'])
def api_shelves_create():
    data = request.get_json(silent=True)
    if not data:
        abort(400, description="JSON request body required")
    try:
        shelf = entity_service.create_shelf(data)
        return jsonify(shelf), 201
    except ValueError as e:
        abort(400, description=str(e))
    except Exception as e:
        current_app.logger.error(f"create_shelf: {e}")
        abort(500)


# ---------------------------------------------------------------------------
# API — detail + update + delete
# ---------------------------------------------------------------------------

@shelves_bp.route('/api/shelves/<shelf_id>', methods=['GET'])
def api_shelf_detail(shelf_id):
    shelf = entity_service.get_shelf(shelf_id)
    if shelf is None:
        abort(404, description=f"Shelf '{shelf_id}' not found")
    return jsonify(shelf)


@shelves_bp.route('/api/shelves/<shelf_id>', methods=['PUT'])
def api_shelf_update(shelf_id):
    data = request.get_json(silent=True)
    if not data:
        abort(400, description="JSON request body required")
    try:
        shelf = entity_service.update_shelf(shelf_id, data)
        if shelf is None:
            abort(404, description=f"Shelf '{shelf_id}' not found")
        return jsonify(shelf)
    except ValueError as e:
        abort(400, description=str(e))
    except Exception as e:
        current_app.logger.error(f"update_shelf: {e}")
        abort(500)


@shelves_bp.route('/api/shelves/<shelf_id>', methods=['DELETE'])
def api_shelf_delete(shelf_id):
    if not entity_service.delete_shelf(shelf_id):
        abort(404, description=f"Shelf '{shelf_id}' not found")
    return jsonify({"message": f"Shelf '{shelf_id}' deleted"})
