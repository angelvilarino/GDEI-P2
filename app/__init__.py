"""
Flask application package for FIWARE Smart Store.
"""
from flask import Flask, jsonify, request
from flask_socketio import SocketIO

socketio = SocketIO()


def create_app(config_name="development"):
    """
    Application factory function.

    Args:
        config_name (str): Configuration environment name.

    Returns:
        Flask: Configured Flask application instance.
    """
    app = Flask(__name__)

    # Load configuration
    if config_name == "production":
        from config import ProductionConfig
        app.config.from_object(ProductionConfig)
    else:
        from config import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)

    # Initialize extensions
    socketio.init_app(app, cors_allowed_origins="*")

    # Initialize database
    from database import db
    db.init_app(app)

    # Import models (needed for Flask-Migrate and relationship resolution)
    from app.models import Store, Product, Shelf, InventoryItem, Employee  # noqa: F401

    # Register blueprints
    from app.routes import register_all_blueprints
    register_all_blueprints(app)

    # ------------------------------------------------------------------
    # Global error handlers — uniform JSON format for all endpoints
    # ------------------------------------------------------------------

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": {"code": 400, "message": str(e.description)}}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": {"code": 404, "message": str(e.description)}}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": {"code": 405, "message": "Method not allowed"}}), 405

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.error(f"Internal server error: {e}")
        return jsonify({"error": {"code": 500, "message": "Internal server error"}}), 500

    # ------------------------------------------------------------------
    # Orion notification webhook
    # POST /notify — receives Orion subscription callbacks and re-emits
    # via Socket.IO so connected clients can update the UI in real time.
    # Handles:
    #   • Product.price change  → emits 'product_price_change'
    #   • InventoryItem.stockCount change → emits 'low_stock'
    # ------------------------------------------------------------------

    @app.route('/notify', methods=['POST'])
    def orion_notify():
        payload = request.get_json(silent=True) or {}
        data = payload.get('data', [])
        for entity in data:
            entity_type = entity.get('type')
            entity_id = entity.get('id')

            if entity_type == 'Product' and 'price' in entity:
                raw = entity['price']
                price_val = raw.get('value', raw) if isinstance(raw, dict) else raw
                socketio.emit('product_price_change', {'id': entity_id, 'price': price_val})
                app.logger.info(f"[NOTIFY] Product price change: {entity_id} → {price_val}")

            elif entity_type == 'InventoryItem' and 'stockCount' in entity:
                raw = entity['stockCount']
                stock_val = raw.get('value', raw) if isinstance(raw, dict) else raw
                ref_store = entity.get('refStore')
                ref_store_val = ref_store.get('value', ref_store) if isinstance(ref_store, dict) else ref_store
                socketio.emit('low_stock', {
                    'id': entity_id,
                    'stockCount': stock_val,
                    'refStore': ref_store_val,
                })
                app.logger.info(f"[NOTIFY] Low stock: {entity_id} → {stock_val}")

        return '', 204

    # Register context providers and subscriptions
    register_context_providers(app)

    return app


def register_context_providers(app):
    """
    Register context providers and subscriptions with Orion.
    Called at application startup.
    """
    with app.app_context():
        from app.db_or_orion import check_orion_connectivity, get_active_backend

        backend = get_active_backend()
        app.logger.info(f" [STARTUP] Active backend: {backend}")

