"""
Routes package — aggregates all entity blueprints and exposes
register_all_blueprints() for use by the application factory.
"""
from flask import Blueprint, render_template
from app.services import entity_service

from app.routes.stores import stores_bp
from app.routes.products import products_bp
from app.routes.employees import employees_bp
from app.routes.shelves import shelves_bp
from app.routes.inventory import inventory_bp

main_bp = Blueprint('main', __name__)


def generate_uml_diagram():
    """
    Generate a Mermaid UML entity relationship diagram dynamically.
    Shows all entities and their relationships.
    
    Returns:
        str: Mermaid diagram markup
    """
    diagram = """erDiagram
    STORE ||--o{ SHELF : "1..N"
    STORE ||--o{ EMPLOYEE : "1..N"
    STORE ||--o{ INVENTORY_ITEM : "1..N"
    SHELF ||--o{ INVENTORY_ITEM : "1..N"
    PRODUCT ||--o{ INVENTORY_ITEM : "1..N"
    
    STORE {
        string id PK
        string name
        string address
        string location
        string image
        string countryCode
        float temperature
        float relativeHumidity
    }
    
    PRODUCT {
        string id PK
        string name
        string size
        float price
        string color
        string originCountry
    }
    
    SHELF {
        string id PK
        string name
        int maxCapacity
        string refStore FK
    }
    
    INVENTORY_ITEM {
        string id PK
        string refStore FK
        string refShelf FK
        string refProduct FK
        int stockCount
        int shelfCount
    }
    
    EMPLOYEE {
        string id PK
        string name
        string image
        string role
        string email
    }
    """
    return diagram


@main_bp.route('/')
def home():
    """
    Home page with statistics and UML diagram.
    Retrieves counts of all entities from database.
    """
    stats = {
        'stores': len(entity_service.get_stores()),
        'products': len(entity_service.get_products()),
        'employees': len(entity_service.get_employees()),
        'inventory_items': len(entity_service.get_inventory_items()),
    }
    
    uml_diagram = generate_uml_diagram()
    
    return render_template('home.html', stats=stats, uml_diagram=uml_diagram)


def register_all_blueprints(app):
    """Register every blueprint on the Flask application."""
    for bp in (main_bp, stores_bp, products_bp, employees_bp, shelves_bp, inventory_bp):
        app.register_blueprint(bp)

