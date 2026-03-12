"""
Routes package — aggregates all entity blueprints and exposes
register_all_blueprints() for use by the application factory.
"""
from flask import Blueprint
from app.db_or_orion import is_orion_active

from app.routes.stores import stores_bp
from app.routes.products import products_bp
from app.routes.employees import employees_bp
from app.routes.shelves import shelves_bp
from app.routes.inventory import inventory_bp

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home():
    backend = 'Orion' if is_orion_active() else 'SQLite'
    return (
        f"FIWARE Smart Store — backend: {backend}. "
        "Views: /stores /products /employees | "
        "API: /api/stores /api/products /api/employees /api/shelves /api/inventory"
    ), 200


def register_all_blueprints(app):
    """Register every blueprint on the Flask application."""
    for bp in (main_bp, stores_bp, products_bp, employees_bp, shelves_bp, inventory_bp):
        app.register_blueprint(bp)

