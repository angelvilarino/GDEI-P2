"""
Main entry point for FIWARE Smart Store Flask application.
Initializes and starts the Flask server with SocketIO support.
"""
import os
import logging
from app import create_app, socketio
from database import db, init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_application():
    """
    Create and configure the Flask application.
    
    Returns:
        Flask: Configured Flask application instance.
    """
    config_name = os.environ.get("FLASK_ENV", "development")
    app = create_app(config_name)
    
    # Initialize database
    with app.app_context():
        init_db(app)
    
    return app


if __name__ == "__main__":
    app = create_application()
    
    logger.info(" [STARTUP] Starting FIWARE Smart Store Flask application...")
    logger.info(f" [STARTUP] Environment: {os.environ.get('FLASK_ENV', 'development')}")
    
    # Run with SocketIO support
    host = os.environ.get("FLASK_HOST", "0.0.0.0")
    port = int(os.environ.get("FLASK_PORT", 5000))
    debug = os.environ.get("FLASK_ENV") == "development"
    
    socketio.run(
        app,
        host=host,
        port=port,
        debug=debug,
        use_reloader=debug,
        allow_unsafe_werkzeug=debug
    )
