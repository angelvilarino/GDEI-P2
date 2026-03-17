"""
Products: web views + REST API endpoints.
Supports GET /api/products?excludeShelf=<id> for dynamic selectors.
"""
from flask import Blueprint, jsonify, request, abort, current_app, render_template
from app.services import entity_service

products_bp = Blueprint('products', __name__)


# ---------------------------------------------------------------------------
# Views (text placeholder — HTML templates to be added in Issue #4)
# ---------------------------------------------------------------------------

@products_bp.route('/products')
def products_list():
    return render_template('products/list.html')


@products_bp.route('/products/<product_id>')
def product_detail(product_id):
    product = entity_service.get_product(product_id)
    if product is None:
        abort(404, description=f"Product '{product_id}' not found")
    inventory_groups = entity_service.get_product_inventory_grouped(product_id)
    return render_template('products/detail.html', product=product, inventory_groups=inventory_groups)


# ---------------------------------------------------------------------------
# API — list + create
# GET /api/products?excludeShelf=<shelf_id>  → products not in that shelf
# ---------------------------------------------------------------------------

@products_bp.route('/api/products', methods=['GET'])
def api_products_list():
    exclude_shelf = request.args.get('excludeShelf')
    return jsonify(entity_service.get_products(exclude_shelf_id=exclude_shelf))


@products_bp.route('/api/products', methods=['POST'])
def api_products_create():
    data = request.get_json(silent=True)
    if not data:
        abort(400, description="JSON request body required")
    try:
        product = entity_service.create_product(data)
        return jsonify(product), 201
    except ValueError as e:
        abort(400, description=str(e))
    except Exception as e:
        current_app.logger.error(f"create_product: {e}")
        abort(500)


# ---------------------------------------------------------------------------
# API — detail + update + delete
# ---------------------------------------------------------------------------

@products_bp.route('/api/products/<product_id>', methods=['GET'])
def api_product_detail(product_id):
    product = entity_service.get_product(product_id)
    if product is None:
        abort(404, description=f"Product '{product_id}' not found")
    return jsonify(product)


@products_bp.route('/api/products/<product_id>', methods=['PUT'])
def api_product_update(product_id):
    data = request.get_json(silent=True)
    if not data:
        abort(400, description="JSON request body required")
    try:
        product = entity_service.update_product(product_id, data)
        if product is None:
            abort(404, description=f"Product '{product_id}' not found")
        return jsonify(product)
    except ValueError as e:
        abort(400, description=str(e))
    except Exception as e:
        current_app.logger.error(f"update_product: {e}")
        abort(500)


@products_bp.route('/api/products/<product_id>', methods=['DELETE'])
def api_product_delete(product_id):
    if not entity_service.delete_product(product_id):
        abort(404, description=f"Product '{product_id}' not found")
    return jsonify({"message": f"Product '{product_id}' deleted"})
