"""
Configuration for FIWARE Smart Store application.
Supports development, testing, and production environments.
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class with common settings."""
    
    # Flask settings
    SECRET_KEY = os.environ.get("SECRET_KEY") or "CHANGE_ME_IN_PRODUCTION"
    DEBUG = False
    TESTING = False
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    
    # SQLAlchemy settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_ECHO = False
    
    # FIWARE Orion settings
    ORION_HOST = os.environ.get("ORION_HOST") or "localhost"
    ORION_PORT = int(os.environ.get("ORION_PORT") or 1026)
    ORION_URL = f"http://{ORION_HOST}:{ORION_PORT}"
    ORION_TIMEOUT = 5  # seconds
    
    # Context provider settings
    CONTEXT_PROVIDER_HOST = os.environ.get("CONTEXT_PROVIDER_HOST") or "localhost"
    CONTEXT_PROVIDER_PORT = int(os.environ.get("CONTEXT_PROVIDER_PORT") or 3000)

    # Orion subscriptions settings
    LOW_STOCK_THRESHOLD = int(os.environ.get("LOW_STOCK_THRESHOLD") or 5)
    
    # SocketIO settings
    SOCKETIO_MESSAGE_QUEUE = None
    SOCKETIO_CORS_ALLOWED_ORIGINS = "*"
    
    # Logging
    LOG_LEVEL = "INFO"


class DevelopmentConfig(Config):
    """Configuration for development environment."""
    DEBUG = True
    TESTING = False
    SESSION_COOKIE_SECURE = False
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///smart_store.db"
    LOG_LEVEL = "DEBUG"


class TestingConfig(Config):
    """Configuration for testing environment."""
    DEBUG = True
    TESTING = True
    SESSION_COOKIE_SECURE = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Configuration for production environment."""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///smart_store.db"
    )
    LOG_LEVEL = "WARNING"
