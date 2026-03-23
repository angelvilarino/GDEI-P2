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


# ---------------------------------------------------------------------------
# Proxy /v2/entities para "Comprar Unidad" (PATCH $inc)
# ---------------------------------------------------------------------------

@inventory_bp.route('/v2/entities/<item_id>/attrs', methods=['PATCH'])
def proxy_v2_patch(item_id):
    data = request.get_json(silent=True)
    if not data:
        abort(400, description="JSON body required")
        
    if entity_service.is_orion_active():
        import requests
        url = f"{current_app.config.get('ORION_URL', 'http://localhost:1026')}/v2/entities/{item_id}/attrs"
        try:
            r = requests.patch(url, json=data)
            return r.content, r.status_code, r.headers.items()
        except requests.exceptions.RequestException as e:
            abort(502, description=f"Error contacting Orion: {str(e)}")
    else:
        # Fallback SQL para emular $inc
        item = entity_service.get_inventory_item(item_id)
        if not item:
            abort(404)
        updates = {}
        for k, v in data.items():
            if isinstance(v, dict) and 'value' in v and isinstance(v['value'], dict) and '$inc' in v['value']:
                inc_val = v['value']['$inc']
                current_val = item.get(k, 0)
                updates[k] = max(0, current_val + inc_val)
            elif isinstance(v, dict) and 'value' in v:
                updates[k] = v['value']
            else:
                updates[k] = v
        entity_service.update_inventory_item(item_id, updates)
        return jsonify({}), 204
