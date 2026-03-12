"""
Database initialization and configuration for FIWARE Smart Store.
Uses SQLAlchemy as ORM.
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    """
    Initialize database with application context.
    Creates all tables defined in models.
    
    Args:
        app (Flask): Flask application instance.
    """
    with app.app_context():
        db.create_all()
