"""
Inventory REST API endpoints.
Supports GET /api/inventory?store=<id>&shelf=<id> for filtered queries.
"""
from flask import Blueprint, jsonify, request, abort, current_app
from app.services import entity_service

inventory_bp = Blueprint('inventory', __name__)


# ---------------------------------------------------------------------------
# API — list + create
# GET /api/inventory?store=<store_id>&shelf=<shelf_id>
# ---------------------------------------------------------------------------

@inventory_bp.route('/api/inventory', methods=['GET'])
def api_inventory_list():
    store_id = request.args.get('store')
    shelf_id = request.args.get('shelf')
    product_id = request.args.get('product')
    return jsonify(entity_service.get_inventory_items(store_id=store_id, shelf_id=shelf_id, product_id=product_id))


@inventory_bp.route('/api/inventory', methods=['POST'])
def api_inventory_create():
    data = request.get_json(silent=True)
    if not data:
        abort(400, description="JSON request body required")
    try:
        item = entity_service.create_inventory_item(data)
        return jsonify(item), 201
    except ValueError as e:
        abort(400, description=str(e))
    except Exception as e:
        current_app.logger.error(f"create_inventory_item: {e}")
        abort(500)


# ---------------------------------------------------------------------------
# API — detail + update + delete
# ---------------------------------------------------------------------------

@inventory_bp.route('/api/inventory/<item_id>', methods=['GET'])
def api_inventory_detail(item_id):
    item = entity_service.get_inventory_item(item_id)
    if item is None:
        abort(404, description=f"InventoryItem '{item_id}' not found")
    return jsonify(item)


@inventory_bp.route('/api/inventory/<item_id>', methods=['PUT'])
def api_inventory_update(item_id):
    data = request.get_json(silent=True)
    if not data:
        abort(400, description="JSON request body required")
    try:
        item = entity_service.update_inventory_item(item_id, data)
        if item is None:
            abort(404, description=f"InventoryItem '{item_id}' not found")
        return jsonify(item)
    except ValueError as e:
        abort(400, description=str(e))
    except Exception as e:
        current_app.logger.error(f"update_inventory_item: {e}")
        abort(500)


@inventory_bp.route('/api/inventory/<item_id>', methods=['DELETE'])
def api_inventory_delete(item_id):
    if not entity_service.delete_inventory_item(item_id):
        abort(404, description=f"InventoryItem '{item_id}' not found")
    return jsonify({"message": f"InventoryItem '{item_id}' deleted"})


@inventory_bp.route('/api/inventory/<item_id>/buy', methods=['PATCH'])
def api_inventory_buy_unit(item_id):
    try:
        item = entity_service.buy_inventory_unit(item_id)
        if item is None:
            abort(404, description=f"InventoryItem '{item_id}' not found")
        return jsonify(item)
    except ValueError as e:
        abort(400, description=str(e))
    except Exception as e:
        current_app.logger.error(f"buy_inventory_unit: {e}")
        abort(500)
