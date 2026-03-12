"""
Flask application package for FIWARE Smart Store.
"""
from flask import Flask
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
    
    # Import models for Flask-Migrate
    from app.models import Store, Product, Shelf, InventoryItem, Employee
    
    # Register blueprints (empty for now)
    # from app.routes import main_bp, api_bp
    # app.register_blueprint(main_bp)
    # app.register_blueprint(api_bp)
    
    # Register context functions
    register_context_providers(app)
    
    return app


def register_context_providers(app):
    """
    Register context providers and subscriptions with Orion.
    This function is called at application startup.
    
    Args:
        app (Flask): Flask application instance.
    """
    with app.app_context():
        from app.db_or_orion import check_orion_connectivity, get_active_backend
        
        backend = get_active_backend()
        app.logger.info(f" [STARTUP] Active backend: {backend}")
