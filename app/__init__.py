"""
Flask application package for FIWARE Smart Store.
"""
import os
from datetime import datetime, timezone

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
    # ------------------------------------------------------------------

    @app.route('/notify', methods=['POST'])
    def orion_notify():
        from app.services import entity_service

        payload = request.get_json(silent=True) or {}
        data = payload.get('data', [])
        threshold = int(app.config.get('LOW_STOCK_THRESHOLD', 5))

        for entity in data:
            entity_type = _extract_value(entity.get('type'))
            entity_id = _extract_value(entity.get('id'))

            if not entity_type or not entity_id:
                continue

            if entity_type == 'Product' and 'price' in entity:
                price_val = _extract_value(entity.get('price'))
                product_name = _extract_value(entity.get('name'))
                if product_name is None:
                    product_name = (entity_service.get_product(entity_id) or {}).get('name')

                event_payload = {
                    'productId': entity_id,
                    'name': product_name,
                    'price': price_val,
                    'timestamp': _now_iso(),
                }
                socketio.emit('product_price_change', event_payload)
                app.logger.info(f"[NOTIFY] Product price change: {entity_id} -> {price_val}")
                continue

            if entity_type == 'InventoryItem' and 'stockCount' in entity:
                stock_val = _extract_value(entity.get('stockCount'))
                try:
                    numeric_stock = int(float(stock_val))
                except (TypeError, ValueError):
                    app.logger.warning(f"[NOTIFY] Invalid stockCount for {entity_id}: {stock_val}")
                    continue

                if numeric_stock >= threshold:
                    app.logger.info(
                        f"[NOTIFY] Ignored InventoryItem notification above threshold: {entity_id} -> {numeric_stock}"
                    )
                    continue

                ref_store_val = _extract_value(entity.get('refStore'))
                ref_product_val = _extract_value(entity.get('refProduct'))
                ref_shelf_val = _extract_value(entity.get('refShelf'))

                item = entity_service.get_inventory_item(entity_id) or {}
                store_id = ref_store_val or item.get('refStore')
                product_id = ref_product_val or item.get('refProduct')
                shelf_id = ref_shelf_val or item.get('refShelf')

                store_name = (entity_service.get_store(store_id) or {}).get('name') if store_id else None
                product_name = (entity_service.get_product(product_id) or {}).get('name') if product_id else None

                event_payload = {
                    'inventoryItemId': entity_id,
                    'stockCount': numeric_stock,
                    'threshold': threshold,
                    'storeId': store_id,
                    'storeName': store_name,
                    'productId': product_id,
                    'productName': product_name,
                    'shelfId': shelf_id,
                    'timestamp': _now_iso(),
                }
                socketio.emit('low_stock', event_payload)
                app.logger.info(f"[NOTIFY] Low stock: {entity_id} -> {numeric_stock}")

        return '', 204

    # ------------------------------------------------------------------
    # Health check endpoint
    # ------------------------------------------------------------------

    @app.route('/health', methods=['GET'])
    def health_check():
        from app.db_or_orion import check_orion_connectivity

        orion_available = check_orion_connectivity(
            app.config.get('ORION_URL', 'http://localhost:1026'),
            app.config.get('ORION_TIMEOUT', 5)
        )

        if orion_available:
            return jsonify({"status": "ok"}), 200
        return jsonify({"status": "error"}), 503

    # Register context providers and subscriptions
    register_context_providers(app)
    register_orion_subscriptions(app)

    return app


def register_context_providers(app):
    """
    Register context providers with Orion.
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


def register_orion_subscriptions(app):
    """Register Orion subscriptions idempotently when Orion is available."""
    with app.app_context():
        from app.db_or_orion import get_active_backend
        from app.services import orion_client

        backend = get_active_backend(
            app.config.get('ORION_URL', 'http://localhost:1026'),
            app.config.get('ORION_TIMEOUT', 5),
        )
        if backend != 'orion':
            app.logger.info(" [STARTUP] Orion unavailable, skipping subscription registration")
            return

        threshold = int(app.config.get('LOW_STOCK_THRESHOLD', 5))
        notify_url = _build_notify_url()

        try:
            subscriptions = _fetch_all_subscriptions(orion_client)
        except Exception as e:
            app.logger.warning(f" [STARTUP] Could not list Orion subscriptions: {e}")
            subscriptions = []

        subscription_definitions = [
            {
                'description': 'smart-store-subscription-product-price-change',
                'subject': {
                    'entities': [{'idPattern': '.*', 'type': 'Product'}],
                    'condition': {'attrs': ['price']},
                },
                'notification': {
                    'http': {'url': notify_url},
                    'attrs': ['id', 'type', 'name', 'price'],
                    'attrsFormat': 'keyValues',
                },
            },
            {
                'description': 'smart-store-subscription-inventory-low-stock',
                'subject': {
                    'entities': [{'idPattern': '.*', 'type': 'InventoryItem'}],
                    'condition': {
                        'attrs': ['stockCount'],
                        'expression': {'q': f'stockCount<{threshold}'},
                    },
                },
                'notification': {
                    'http': {'url': notify_url},
                    'attrs': ['id', 'type', 'refStore', 'refProduct', 'refShelf', 'stockCount'],
                    'attrsFormat': 'keyValues',
                },
            },
        ]

        for sub in subscription_definitions:
            if _subscription_exists(subscriptions, sub['description'], sub['subject'], notify_url):
                app.logger.info(f" [STARTUP] Subscription already exists ({sub['description']})")
                continue

            payload = {
                'description': sub['description'],
                'subject': sub['subject'],
                'notification': sub['notification'],
                'throttling': 0,
            }

            try:
                sub_id = orion_client.create_subscription(payload)
                if sub_id:
                    app.logger.info(f" [STARTUP] Registered subscription {sub['description']} with id {sub_id}")
                else:
                    app.logger.info(f" [STARTUP] Registered subscription {sub['description']}")
            except Exception as e:
                app.logger.warning(f" [STARTUP] Subscription registration failed ({sub['description']}): {e}")


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


def _fetch_all_subscriptions(orion_client_module):
    subscriptions = []
    limit = 100
    offset = 0
    while True:
        chunk = orion_client_module.get_subscriptions(limit=limit, offset=offset)
        if not chunk:
            break
        subscriptions.extend(chunk)
        if len(chunk) < limit:
            break
        offset += limit
    return subscriptions


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


def _subscription_exists(subscriptions, description, expected_subject, notify_url):
    expected_url = (notify_url or '').rstrip('/')
    expected_signature = _subject_signature(expected_subject)

    for subscription in subscriptions:
        status = str((subscription or {}).get('status', 'active')).lower()
        if status in {'inactive', 'failed', 'expired'}:
            continue

        sub_description = (subscription or {}).get('description')
        sub_notification = (subscription or {}).get('notification') or {}
        sub_url = (((sub_notification.get('http') or {}).get('url')) or '').rstrip('/')
        sub_signature = _subject_signature((subscription or {}).get('subject') or {})

        if sub_description == description:
            return True
        if sub_url == expected_url and sub_signature == expected_signature:
            return True

    return False


def _subject_signature(subject):
    entities = (subject or {}).get('entities') or []
    condition = (subject or {}).get('condition') or {}
    cond_attrs = tuple(sorted(condition.get('attrs') or []))
    expression_q = ((condition.get('expression') or {}).get('q')) or ''

    entity_signature = tuple(sorted(
        (
            (entity or {}).get('type') or '',
            (entity or {}).get('id') or '',
            (entity or {}).get('idPattern') or '',
        )
        for entity in entities
    ))

    return entity_signature, cond_attrs, expression_q


def _extract_value(raw):
    if isinstance(raw, dict) and 'value' in raw:
        return raw['value']
    return raw


def _build_notify_url():
    flask_port = os.environ.get('FLASK_PORT', '5000')
    return f"http://host.docker.internal:{flask_port}/notify"


def _now_iso():
    return datetime.now(timezone.utc).isoformat()

