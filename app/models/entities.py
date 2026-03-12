"""
SQLAlchemy models for FIWARE Smart Store entities.

Entities:
- Store: Physical retail unit
- Product: Sellable product
- Shelf: Storage unit within a Store
- InventoryItem: Operational relationship between Store, Shelf, Product with quantities
- Employee: Person employed in a Store
"""
from datetime import datetime
from database import db


class Store(db.Model):
    """Store entity: physical retail unit."""
    __tablename__ = 'store'
    
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(500), nullable=True)
    location = db.Column(db.String(255), nullable=True)  # geo:json Point as string [lon, lat]
    image = db.Column(db.String(500), nullable=True)
    url = db.Column(db.String(500), nullable=True)
    telephone = db.Column(db.String(20), nullable=True)
    countryCode = db.Column(db.String(2), nullable=False)
    capacity = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text, nullable=True)
    temperature = db.Column(db.Float, nullable=True)  # From external provider
    relativeHumidity = db.Column(db.Float, nullable=True)  # From external provider
    tweets = db.Column(db.JSON, nullable=True, default=list)  # From external provider
    
    # Relationships
    shelves = db.relationship('Shelf', backref='store', lazy=True, cascade='all, delete-orphan')
    employees = db.relationship('Employee', backref='store', lazy=True, cascade='all, delete-orphan')
    inventory_items = db.relationship('InventoryItem', backref='store', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'location': self.location,
            'image': self.image,
            'url': self.url,
            'telephone': self.telephone,
            'countryCode': self.countryCode,
            'capacity': self.capacity,
            'description': self.description,
            'temperature': self.temperature,
            'relativeHumidity': self.relativeHumidity,
            'tweets': self.tweets or [],
        }

    def __repr__(self):
        return f'<Store {self.id}: {self.name}>'


class Product(db.Model):
    """Product entity: commercializable product."""
    __tablename__ = 'product'
    
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    size = db.Column(db.String(10), nullable=True)  # S, M, L, XL
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(500), nullable=True)
    originCountry = db.Column(db.String(3), nullable=True)
    color = db.Column(db.String(7), nullable=True)  # Hex color #RRGGBB
    
    # Relationships
    inventory_items = db.relationship('InventoryItem', backref='product', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'size': self.size,
            'price': self.price,
            'image': self.image,
            'originCountry': self.originCountry,
            'color': self.color,
        }

    def __repr__(self):
        return f'<Product {self.id}: {self.name}>'


class Shelf(db.Model):
    """Shelf entity: storage unit within a Store."""
    __tablename__ = 'shelf'
    
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    maxCapacity = db.Column(db.Integer, nullable=False)
    refStore = db.Column(db.String(50), db.ForeignKey('store.id'), nullable=False)
    
    # Relationships
    inventory_items = db.relationship('InventoryItem', backref='shelf', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'maxCapacity': self.maxCapacity,
            'refStore': self.refStore,
        }

    def __repr__(self):
        return f'<Shelf {self.id}: {self.name}>'


class InventoryItem(db.Model):
    """InventoryItem entity: operational relationship between Store, Shelf, Product."""
    __tablename__ = 'inventory_item'
    
    id = db.Column(db.String(50), primary_key=True)
    refStore = db.Column(db.String(50), db.ForeignKey('store.id'), nullable=False)
    refShelf = db.Column(db.String(50), db.ForeignKey('shelf.id'), nullable=False)
    refProduct = db.Column(db.String(50), db.ForeignKey('product.id'), nullable=False)
    stockCount = db.Column(db.Integer, nullable=False, default=0)
    shelfCount = db.Column(db.Integer, nullable=False, default=0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'refStore': self.refStore,
            'refShelf': self.refShelf,
            'refProduct': self.refProduct,
            'stockCount': self.stockCount,
            'shelfCount': self.shelfCount,
        }

    def __repr__(self):
        return f'<InventoryItem {self.id}>'


class Employee(db.Model):
    """Employee entity: person employed in a Store."""
    __tablename__ = 'employee'
    
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(500), nullable=True)
    salary = db.Column(db.Float, nullable=True)
    role = db.Column(db.String(100), nullable=True)  # Manager, Cashier, Stock, etc.
    refStore = db.Column(db.String(50), db.ForeignKey('store.id'), nullable=False)
    email = db.Column(db.String(255), nullable=True, unique=True)
    dateOfContract = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    skills = db.Column(db.JSON, nullable=True, default=list)  # Array of skills
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)  # Hashed password
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'image': self.image,
            'salary': self.salary,
            'role': self.role,
            'refStore': self.refStore,
            'email': self.email,
            'dateOfContract': self.dateOfContract.isoformat() if self.dateOfContract else None,
            'skills': self.skills or [],
            'username': self.username,
            # password excluded from serialization
        }

    def __repr__(self):
        return f'<Employee {self.id}: {self.name}>'
