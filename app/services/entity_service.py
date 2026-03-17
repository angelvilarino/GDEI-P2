"""
Unified CRUD service for all entities.
Dispatches to SQLite (SQLAlchemy) or Orion (NGSIv2) based on active backend.

All public functions return plain dicts (or lists of dicts) so routes remain
backend-agnostic.  Entity ids follow the pattern urn:ngsi-ld:<Type>:<hex12>.
"""
import uuid as _uuid
from datetime import datetime
from werkzeug.security import generate_password_hash

from app.db_or_orion import is_orion_active
from app.models.entities import Store, Product, Shelf, InventoryItem, Employee
from database import db
from app.services import orion_client


# ---------------------------------------------------------------------------
# ID generation
# ---------------------------------------------------------------------------

def _new_id(entity_type):
    return f"urn:ngsi-ld:{entity_type}:{_uuid.uuid4().hex[:12]}"


# ---------------------------------------------------------------------------
# NGSIv2 attribute type maps  (used only for write payloads sent to Orion)
# ---------------------------------------------------------------------------

_NGSI_TYPES = {
    'Store': {
        'name': 'Text', 'address': 'PostalAddress', 'location': 'geo:json',
        'image': 'Text', 'url': 'Text', 'telephone': 'Text',
        'countryCode': 'Text', 'capacity': 'Integer', 'description': 'Text',
        'temperature': 'Number', 'relativeHumidity': 'Number', 'tweets': 'Array',
    },
    'Product': {
        'name': 'Text', 'size': 'Text', 'price': 'Number',
        'image': 'Text', 'originCountry': 'Text', 'color': 'Text',
    },
    'Shelf': {
        'name': 'Text', 'maxCapacity': 'Integer',
        'location': 'Text', 'refStore': 'Relationship',
    },
    'InventoryItem': {
        'refStore': 'Relationship', 'refShelf': 'Relationship',
        'refProduct': 'Relationship',
        'stockCount': 'Integer', 'shelfCount': 'Integer',
    },
    'Employee': {
        'name': 'Text', 'image': 'Text', 'salary': 'Number', 'role': 'Text',
        'refStore': 'Relationship', 'email': 'Text', 'gender': 'Text',
        'dateOfContract': 'DateTime', 'skills': 'Array', 'username': 'Text',
        # password intentionally omitted — never stored in Orion
    },
}


def _sanitize_orion_value(value):
    """Strip characters forbidden by Orion NGSIv2 from string attribute values.

    Orion forbids: < > " ' ; ( ) = ? & in attribute values.
    For HTTP(S) URLs the query string is stripped transparently so the base
    URL is stored while the frontend can keep using decorated CDN links.
    """
    if not isinstance(value, str):
        return value
    if value.startswith(('http://', 'https://')):
        idx = value.find('?')
        if idx != -1:
            return value[:idx]
    return value


def _to_ngsi(entity_type, entity_id, data):
    """Build full NGSIv2 entity dict for POST /v2/entities."""
    attr_types = _NGSI_TYPES.get(entity_type, {})
    ngsi = {'id': entity_id, 'type': entity_type}
    for key, value in data.items():
        if key in ('id', 'type') or value is None:
            continue
        ngsi[key] = {'type': attr_types.get(key, 'Text'), 'value': _sanitize_orion_value(value)}
    return ngsi


def _to_ngsi_attrs(entity_type, data):
    """Build NGSIv2 attrs dict for PATCH /v2/entities/<id>/attrs."""
    attr_types = _NGSI_TYPES.get(entity_type, {})
    attrs = {}
    for key, value in data.items():
        if key in ('id', 'type') or value is None:
            continue
        attrs[key] = {'type': attr_types.get(key, 'Text'), 'value': _sanitize_orion_value(value)}
    return attrs


def _ngsi_val(raw):
    """Extract plain value from NGSIv2 attribute (works with both full and keyValues)."""
    if isinstance(raw, dict) and 'value' in raw:
        return raw['value']
    return raw


def _orion_to_flat(entity, exclude=None):
    """Convert Orion entity dict (keyValues or full) to uniform flat dict."""
    skip = {'type', '@context'}
    if exclude:
        skip.update(exclude)
    result = {}
    for key, val in entity.items():
        if key in skip:
            continue
        result[key] = _ngsi_val(val)
    return result


# ===========================================================================
#  STORES
# ===========================================================================

def get_stores():
    if is_orion_active():
        return [_orion_to_flat(e) for e in orion_client.get_entities('Store')]
    return [s.to_dict() for s in Store.query.order_by(Store.name).all()]


def get_store(store_id):
    if is_orion_active():
        e = orion_client.get_entity(store_id)
        return _orion_to_flat(e) if e else None
    s = db.session.get(Store, store_id)
    return s.to_dict() if s else None


def create_store(data):
    if not data.get('name') or not data.get('countryCode'):
        raise ValueError("Fields 'name' and 'countryCode' are required")
    store_id = data.get('id') or _new_id('Store')
    if is_orion_active():
        orion_client.create_entity(_to_ngsi('Store', store_id, data))
        return {**data, 'id': store_id}
    store = Store(
        id=store_id, name=data['name'],
        address=data.get('address'), location=data.get('location'),
        image=data.get('image'), url=data.get('url'),
        telephone=data.get('telephone'), countryCode=data['countryCode'],
        capacity=data.get('capacity'), description=data.get('description'),
        temperature=data.get('temperature'), relativeHumidity=data.get('relativeHumidity'),
        tweets=data.get('tweets'),
    )
    db.session.add(store)
    db.session.commit()
    return store.to_dict()


def update_store(store_id, data):
    if is_orion_active():
        attrs = _to_ngsi_attrs('Store', {k: v for k, v in data.items() if k not in ('id', 'type')})
        if not orion_client.update_entity_attrs(store_id, attrs):
            return None
        e = orion_client.get_entity(store_id)
        return _orion_to_flat(e) if e else None
    store = db.session.get(Store, store_id)
    if not store:
        return None
    _update_fields(store, data, (
        'name', 'address', 'location', 'image', 'url', 'telephone',
        'countryCode', 'capacity', 'description', 'temperature', 'relativeHumidity', 'tweets',
    ))
    db.session.commit()
    return store.to_dict()


def delete_store(store_id):
    if is_orion_active():
        return orion_client.delete_entity(store_id)
    store = db.session.get(Store, store_id)
    if not store:
        return False
    db.session.delete(store)
    db.session.commit()
    return True


# ===========================================================================
#  PRODUCTS
# ===========================================================================

def get_products(exclude_shelf_id=None):
    if is_orion_active():
        entities = orion_client.get_entities('Product')
        products = [_orion_to_flat(e) for e in entities]
        if exclude_shelf_id:
            items = orion_client.get_entities(
                'InventoryItem',
                extra_params={'q': f'refShelf=={exclude_shelf_id}'},
            )
            excluded = {_ngsi_val(i.get('refProduct', {})) for i in items}
            products = [p for p in products if p['id'] not in excluded]
        return products
    query = Product.query
    if exclude_shelf_id:
        query = query.filter(
            ~Product.inventory_items.any(InventoryItem.refShelf == exclude_shelf_id)
        )
    return [p.to_dict() for p in query.order_by(Product.name).all()]


def get_product(product_id):
    if is_orion_active():
        e = orion_client.get_entity(product_id)
        return _orion_to_flat(e) if e else None
    p = db.session.get(Product, product_id)
    return p.to_dict() if p else None


def create_product(data):
    if not data.get('name') or data.get('price') is None:
        raise ValueError("Fields 'name' and 'price' are required")
    product_id = data.get('id') or _new_id('Product')
    if is_orion_active():
        orion_client.create_entity(_to_ngsi('Product', product_id, data))
        return {**data, 'id': product_id}
    product = Product(
        id=product_id, name=data['name'], price=float(data['price']),
        size=data.get('size'), image=data.get('image'),
        originCountry=data.get('originCountry'), color=data.get('color'),
    )
    db.session.add(product)
    db.session.commit()
    return product.to_dict()


def update_product(product_id, data):
    if is_orion_active():
        attrs = _to_ngsi_attrs('Product', {k: v for k, v in data.items() if k not in ('id', 'type')})
        if not orion_client.update_entity_attrs(product_id, attrs):
            return None
        e = orion_client.get_entity(product_id)
        return _orion_to_flat(e) if e else None
    product = db.session.get(Product, product_id)
    if not product:
        return None
    _update_fields(product, data, ('name', 'price', 'size', 'image', 'originCountry', 'color'))
    db.session.commit()
    return product.to_dict()


def delete_product(product_id):
    if is_orion_active():
        return orion_client.delete_entity(product_id)
    product = db.session.get(Product, product_id)
    if not product:
        return False
    db.session.delete(product)
    db.session.commit()
    return True


# ===========================================================================
#  EMPLOYEES
# ===========================================================================

def get_employees():
    if is_orion_active():
        return [_orion_to_flat(e, exclude=['password']) for e in orion_client.get_entities('Employee')]
    return [e.to_dict() for e in Employee.query.order_by(Employee.name).all()]


def get_employee(employee_id):
    if is_orion_active():
        e = orion_client.get_entity(employee_id)
        return _orion_to_flat(e, exclude=['password']) if e else None
    emp = db.session.get(Employee, employee_id)
    return emp.to_dict() if emp else None


def create_employee(data):
    for field in ('name', 'refStore', 'username', 'password'):
        if not data.get(field):
            raise ValueError(f"Field '{field}' is required")
    employee_id = data.get('id') or _new_id('Employee')
    hashed_pw = generate_password_hash(data['password'])
    if is_orion_active():
        orion_data = {k: v for k, v in data.items() if k != 'password'}
        orion_client.create_entity(_to_ngsi('Employee', employee_id, orion_data))
        return {**orion_data, 'id': employee_id}
    doc = data.get('dateOfContract')
    employee = Employee(
        id=employee_id, name=data['name'],
        image=data.get('image'), salary=data.get('salary'),
        role=data.get('role'), refStore=data['refStore'],
        email=data.get('email'), gender=data.get('gender'),
        dateOfContract=datetime.fromisoformat(doc) if doc else None,
        skills=data.get('skills', []),
        username=data['username'], password=hashed_pw,
    )
    db.session.add(employee)
    db.session.commit()
    return employee.to_dict()


def update_employee(employee_id, data):
    if is_orion_active():
        orion_data = {k: v for k, v in data.items() if k not in ('id', 'type', 'password')}
        attrs = _to_ngsi_attrs('Employee', orion_data)
        if not orion_client.update_entity_attrs(employee_id, attrs):
            return None
        e = orion_client.get_entity(employee_id)
        return _orion_to_flat(e, exclude=['password']) if e else None
    emp = db.session.get(Employee, employee_id)
    if not emp:
        return None
    _update_fields(emp, data, ('name', 'image', 'salary', 'role', 'refStore', 'email', 'gender', 'skills', 'username'))
    if data.get('password'):
        emp.password = generate_password_hash(data['password'])
    if data.get('dateOfContract'):
        try:
            emp.dateOfContract = datetime.fromisoformat(data['dateOfContract'])
        except (ValueError, TypeError):
            pass
    db.session.commit()
    return emp.to_dict()


def delete_employee(employee_id):
    if is_orion_active():
        return orion_client.delete_entity(employee_id)
    emp = db.session.get(Employee, employee_id)
    if not emp:
        return False
    db.session.delete(emp)
    db.session.commit()
    return True


# ===========================================================================
#  SHELVES
# ===========================================================================

def get_shelves(store_id=None, exclude_product_id=None):
    if is_orion_active():
        extra = {}
        if store_id:
            extra['q'] = f'refStore=={store_id}'
        entities = orion_client.get_entities('Shelf', extra_params=extra or None)
        shelves = [_orion_to_flat(e) for e in entities]
        if exclude_product_id:
            items = orion_client.get_entities(
                'InventoryItem',
                extra_params={'q': f'refProduct=={exclude_product_id}'},
            )
            occupied = {_ngsi_val(i.get('refShelf', {})) for i in items}
            shelves = [s for s in shelves if s['id'] not in occupied]
        return shelves
    query = Shelf.query
    if store_id:
        query = query.filter_by(refStore=store_id)
    if exclude_product_id:
        query = query.filter(
            ~Shelf.inventory_items.any(InventoryItem.refProduct == exclude_product_id)
        )
    return [s.to_dict() for s in query.order_by(Shelf.name).all()]


def get_shelf(shelf_id):
    if is_orion_active():
        e = orion_client.get_entity(shelf_id)
        return _orion_to_flat(e) if e else None
    s = db.session.get(Shelf, shelf_id)
    return s.to_dict() if s else None


def create_shelf(data):
    for field in ('name', 'maxCapacity', 'refStore'):
        if data.get(field) is None:
            raise ValueError(f"Field '{field}' is required")
    shelf_id = data.get('id') or _new_id('Shelf')
    if is_orion_active():
        orion_client.create_entity(_to_ngsi('Shelf', shelf_id, data))
        return {**data, 'id': shelf_id}
    shelf = Shelf(
        id=shelf_id, name=data['name'],
        maxCapacity=int(data['maxCapacity']), refStore=data['refStore'],
    )
    db.session.add(shelf)
    db.session.commit()
    return shelf.to_dict()


def update_shelf(shelf_id, data):
    if is_orion_active():
        attrs = _to_ngsi_attrs('Shelf', {k: v for k, v in data.items() if k not in ('id', 'type')})
        if not orion_client.update_entity_attrs(shelf_id, attrs):
            return None
        e = orion_client.get_entity(shelf_id)
        return _orion_to_flat(e) if e else None
    shelf = db.session.get(Shelf, shelf_id)
    if not shelf:
        return None
    _update_fields(shelf, data, ('name', 'maxCapacity', 'refStore'))
    db.session.commit()
    return shelf.to_dict()


def delete_shelf(shelf_id):
    if is_orion_active():
        return orion_client.delete_entity(shelf_id)
    shelf = db.session.get(Shelf, shelf_id)
    if not shelf:
        return False
    db.session.delete(shelf)
    db.session.commit()
    return True


# ===========================================================================
#  INVENTORY ITEMS
# ===========================================================================

def get_inventory_items(store_id=None, shelf_id=None, product_id=None):
    if is_orion_active():
        conditions = []
        if store_id:
            conditions.append(f'refStore=={store_id}')
        if shelf_id:
            conditions.append(f'refShelf=={shelf_id}')
        if product_id:
            conditions.append(f'refProduct=={product_id}')
        extra = {'q': ';'.join(conditions)} if conditions else None
        entities = orion_client.get_entities('InventoryItem', extra_params=extra)
        return [_orion_to_flat(e) for e in entities]
    query = InventoryItem.query
    if store_id:
        query = query.filter_by(refStore=store_id)
    if shelf_id:
        query = query.filter_by(refShelf=shelf_id)
    if product_id:
        query = query.filter_by(refProduct=product_id)
    return [i.to_dict() for i in query.all()]


def get_product_inventory_grouped(product_id):
    """Return inventory for a product grouped by Store.

    Returns a list of dicts:
      [{"store_id", "store_name", "store_image", "store_country",
        "total_stock", "shelves": [{"item_id", "shelf_id", "shelf_name", "shelfCount"}]}]
    """
    items = get_inventory_items(product_id=product_id)
    if not items:
        return []

    # Collect unique store and shelf ids
    store_ids = list({i['refStore'] for i in items})
    shelf_ids = list({i['refShelf'] for i in items})

    # Fetch store and shelf details
    stores_map = {}
    for sid in store_ids:
        s = get_store(sid)
        if s:
            stores_map[sid] = s

    shelves_map = {}
    for shid in shelf_ids:
        sh = get_shelf(shid)
        if sh:
            shelves_map[shid] = sh

    # Group items by store
    grouped = {}
    for item in items:
        sid = item['refStore']
        if sid not in grouped:
            store = stores_map.get(sid, {})
            grouped[sid] = {
                'store_id': sid,
                'store_name': store.get('name', sid),
                'store_image': store.get('image', ''),
                'store_country': store.get('countryCode', ''),
                'total_stock': 0,
                'shelves': [],
            }
        shelf = shelves_map.get(item['refShelf'], {})
        shelf_count = item.get('shelfCount', 0) or 0
        grouped[sid]['total_stock'] += shelf_count
        grouped[sid]['shelves'].append({
            'item_id': item['id'],
            'shelf_id': item['refShelf'],
            'shelf_name': shelf.get('name', item['refShelf']),
            'shelfCount': shelf_count,
        })

    return sorted(grouped.values(), key=lambda x: x['store_name'])


def get_inventory_item(item_id):
    if is_orion_active():
        e = orion_client.get_entity(item_id)
        return _orion_to_flat(e) if e else None
    item = db.session.get(InventoryItem, item_id)
    return item.to_dict() if item else None


def create_inventory_item(data):
    for field in ('refStore', 'refShelf', 'refProduct'):
        if not data.get(field):
            raise ValueError(f"Field '{field}' is required")
    item_id = data.get('id') or _new_id('InventoryItem')
    if is_orion_active():
        orion_client.create_entity(_to_ngsi('InventoryItem', item_id, data))
        return {**data, 'id': item_id}
    item = InventoryItem(
        id=item_id,
        refStore=data['refStore'], refShelf=data['refShelf'], refProduct=data['refProduct'],
        stockCount=int(data.get('stockCount', 0)),
        shelfCount=int(data.get('shelfCount', 0)),
    )
    db.session.add(item)
    db.session.commit()
    return item.to_dict()


def update_inventory_item(item_id, data):
    if is_orion_active():
        attrs = _to_ngsi_attrs('InventoryItem', {k: v for k, v in data.items() if k not in ('id', 'type')})
        if not orion_client.update_entity_attrs(item_id, attrs):
            return None
        e = orion_client.get_entity(item_id)
        return _orion_to_flat(e) if e else None
    item = db.session.get(InventoryItem, item_id)
    if not item:
        return None
    _update_fields(item, data, ('refStore', 'refShelf', 'refProduct', 'stockCount', 'shelfCount'))
    db.session.commit()
    return item.to_dict()


def delete_inventory_item(item_id):
    if is_orion_active():
        return orion_client.delete_entity(item_id)
    item = db.session.get(InventoryItem, item_id)
    if not item:
        return False
    db.session.delete(item)
    db.session.commit()
    return True


# ===========================================================================
#  Internal helpers
# ===========================================================================

def _update_fields(obj, data, fields):
    """Set attributes on a SQLAlchemy model instance for each field present in data."""
    for field in fields:
        if field in data:
            setattr(obj, field, data[field])
