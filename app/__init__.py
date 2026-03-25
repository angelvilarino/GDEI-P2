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

    # ------------------------------------------------------------------
    # Health check endpoint
    # GET /health — returns connection status to Orion Context Broker
    # ------------------------------------------------------------------

    @app.route('/health', methods=['GET'])
    def health_check():
        """
        Health check endpoint that verifies Orion connectivity.
        
        Returns:
            dict: JSON with status 'ok' if Orion is available, 'error' otherwise.
        """
        from app.db_or_orion import check_orion_connectivity

        orion_available = check_orion_connectivity(
            app.config.get('ORION_URL', 'http://localhost:1026'),
            app.config.get('ORION_TIMEOUT', 5)
        )

        if orion_available:
            return jsonify({"status": "ok"}), 200
        else:
            return jsonify({"status": "error"}), 503

    # Register context providers and subscriptions
    register_context_providers(app)

    return app


def register_context_providers(app):
    """
    Register context providers and subscriptions with Orion.
    Called at application startup.
    """
    with app.app_context():
        from app.db_or_orion import get_active_backend
        from app.services import orion_client

        backend = get_active_backend(
            app.config.get('ORION_URL', 'http://localhost:1026'),
            app.config.get('ORION_TIMEOUT', 5),
        )
        app.logger.info(f" [STARTUP] Active backend: {backend}")

        if backend != 'orion':
            app.logger.info(" [STARTUP] Orion unavailable, skipping provider registration")
            return

        try:
            registrations = _fetch_all_registrations(orion_client)
        except Exception as e:
            app.logger.warning(f" [STARTUP] Could not list Orion registrations: {e}")
            registrations = []

        try:
            stores = orion_client.get_entities('Store', limit=1000)
            store_ids = [store.get('id') for store in stores if store.get('id')]
        except Exception as e:
            app.logger.warning(f" [STARTUP] Could not list Store entities for provider registration: {e}")
            store_ids = []

        if not store_ids:
            app.logger.info(" [STARTUP] No stores found in Orion, skipping provider registration")
            return

        providers = [
            {
                'name': 'weather',
                'entity_type': 'Store',
                'attrs': ['temperature', 'relativeHumidity'],
                'url': 'http://tutorial:3000/random/weatherConditions',
            },
            {
                'name': 'tweets',
                'entity_type': 'Store',
                'attrs': ['tweets'],
                'url': 'http://tutorial:3000/catfacts/tweets',
            },
        ]

        for provider in providers:
            for store_id in store_ids:
                if _registration_exists(
                    registrations,
                    provider['entity_type'],
                    provider['attrs'],
                    provider['url'],
                    entity_id=store_id,
                ):
                    app.logger.info(
                        f" [STARTUP] Provider registration already exists ({provider['name']} | {store_id})"
                    )
                    continue

                payload = {
                    'description': f"smart-store-{provider['name']}-{store_id.split(':')[-1]}",
                    'dataProvided': {
                        'entities': [{'type': provider['entity_type'], 'id': store_id}],
                        'attrs': provider['attrs'],
                    },
                    'provider': {
                        'http': {'url': provider['url']},
                        'supportedForwardingMode': 'all',
                    },
                }

                try:
                    reg_id = orion_client.create_registration(payload)
                    if reg_id:
                        app.logger.info(
                            f" [STARTUP] Registered provider '{provider['name']}' for {store_id} with id {reg_id}"
                        )
                    else:
                        app.logger.info(
                            f" [STARTUP] Registered provider '{provider['name']}' for {store_id}"
                        )
                except Exception as e:
                    app.logger.warning(
                        f" [STARTUP] Provider registration failed ({provider['name']} | {store_id}): {e}"
                    )


def _fetch_all_registrations(orion_client_module):
    registrations = []
    limit = 100
    offset = 0
    while True:
        chunk = orion_client_module.get_registrations(limit=limit, offset=offset)
        if not chunk:
            break
        registrations.extend(chunk)
        if len(chunk) < limit:
            break
        offset += limit
    return registrations


def _registration_exists(registrations, entity_type, attrs, provider_url, entity_id=None):
    attrs_set = set(attrs)
    expected_url = (provider_url or '').rstrip('/')

    for registration in registrations:
        entities = ((registration or {}).get('dataProvided') or {}).get('entities') or []
        reg_attrs = ((registration or {}).get('dataProvided') or {}).get('attrs') or []
        provider = (registration or {}).get('provider') or {}
        reg_url = (((provider.get('http') or {}).get('url')) or '').rstrip('/')
        legacy_forwarding = provider.get('legacyForwarding')

        has_entity = any(
            (e or {}).get('type') == entity_type and (entity_id is None or (e or {}).get('id') == entity_id)
            for e in entities
        )
        has_attrs = attrs_set.issubset(set(reg_attrs))
        has_url = reg_url == expected_url
        is_non_legacy = (legacy_forwarding is False) or (legacy_forwarding is None)
        if has_entity and has_attrs and has_url and is_non_legacy:
            return True

    return False

