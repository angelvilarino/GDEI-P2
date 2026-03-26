# Data Model - FIWARE Smart Store

## Estado de Implementación

- **Documentación del modelo**: ✅ Completada
- **Modelos SQLAlchemy**: ✅ Completada (Issue #2)
- **Población de datos inicial**: ✅ Completada (Issue #2)
- **API REST CRUD**: ✅ Completada (Issue #3) — GET list, GET detail, POST, PUT, DELETE para las 5 entidades
- **Serialización to_dict()**: ✅ Completada (Issue #3) — todos los modelos exponen `to_dict()` en JSON; Employee.to_dict() excluye `password`
- **Plantillas HTML y frontend base**: ✅ Completada (Issue #4) — las entidades se representan en vistas HTML con layout compartido; i18n y tema dark/light persistidos en `localStorage`
- **Vista Home con estadísticas**: ✅ Completada (Issue #5) — página home muestra contadores de todas las entidades y diagrama UML Mermaid; soporte Dark/Light
- **Issue #6 - Integración Orion + vista Products**: ✅ Completada
  - `import-data` carga datos directamente en Orion vía `POST /v2/entities`
  - `start.sh` ejecuta carga inicial solo si Orion está vacío
  - Home consulta contadores desde backend activo (Orion/SQLite) con `entity_service`
  - Vista Products lista/alta/edita/borra productos con validaciones HTML+JS
- **Issue #7 - Vista Stores + consistencia dataset por defecto**: ✅ Completada
  - `start.sh` resetea entidades de Orion y recarga `import-data` en cada arranque
  - Se garantiza restauración de entidades por defecto tras reinicio del entorno
  - Vista Stores implementada con CRUD en tabla/modal y validación HTML+JS
  - `temperature` y `relativeHumidity` se mantienen como atributos externos y no editables en formulario
  - Fallback de imagen para Stores basado en Picsum Photos
  - Traducciones ES/EN completadas para todos los textos de Stores
- **Issue #8 - Vista Employees**: ✅ Completada
  - CRUD de Empleados integrado y operativo.
  - Manejo de hashes para contraseñas de empleado. 
  - Gestión correcta de arrays de strings (skills) dentro de EntityType.
  - Relación Employee -> Store (`refStore`) poblada asíncronamente en los formularios.

- **Issue #9 - Vista detalle de Product**: ✅ Completada
  - `entity_service.get_inventory_items()` acepta `product_id` para filtrar por producto en Orion y SQLite.
  - Nueva función `get_product_inventory_grouped(product_id)` devuelve inventario agrupado por Store: `[{store_id, store_name, store_image, store_country, total_stock, shelves: [{item_id, shelf_id, shelf_name, shelfCount}]}]`.
  - Vista `products/detail.html` con CRUD de InventoryItems (crear, editar shelfCount, borrar) sin recarga de página.
  - `GET /api/shelves?store=<id>&excludeProduct=<id>` usado para filtrar Shelves disponibles al añadir un InventoryItem.
  - API `GET /api/inventory?product=<id>` para refrescar la tabla de inventario desde el cliente.

- **Issue #10 - Vista detalle de Store (InventoryItems por Shelf)**: ✅ Completada
  - `entity_service.get_store_inventory_grouped(store_id)` implementada con salida:
    `[{shelf_id, shelf_name, shelf_location, shelf_maxCapacity, current_count, items:[{item_id, product_id, product_name, product_image, product_price, product_size, product_color, stockCount, shelfCount}]}]`.
  - `GET /stores/<id>` usa Store real + inventario agrupado para render de detalle.
  - API `GET /api/stores/<id>/inventory-grouped` disponible para refresco dinámico de la tabla sin recarga global.
  - Compra unitaria implementada con `PATCH /api/inventory/<id>/buy`:
    - Orion: decremento de `shelfCount` y `stockCount` en attrs,
    - SQLite: decremento equivalente con validación de no negativos.
  - El detalle mantiene bloques preparados para `temperature`, `relativeHumidity` y `tweets` de cara a una issue posterior.

- **Issue #11 - Recorrido inmersivo 3D en detalle Store (Three.js)**: ✅ Completada
  - Sin cambios de esquema ni nuevas entidades.
  - El módulo 3D consume exclusivamente la misma estructura ya disponible en plantilla desde `get_store_inventory_grouped(store_id)`:
    `[{shelf_id, shelf_name, shelf_location, shelf_maxCapacity, current_count, items:[{item_id, product_id, product_name, product_image, product_price, product_size, product_color, stockCount, shelfCount}]}]`.
  - `shelfCount` y `stockCount` pasan a tener representación visual adicional en escena 3D mediante etiquetas, manteniendo su semántica de datos intacta.
  - Se añade representación visual avanzada (pasillos, estanterías realistas y agrupaciones de productos) reutilizando exactamente los campos existentes (`shelf_id`, `shelf_name`, `items[].product_*`, `items[].shelfCount`, `items[].stockCount`) sin cambios de contrato.
  - Etiquetas 3D migradas a render HTML (`CSS2DRenderer`) para mayor nitidez en stock e identificadores, sin modificar estructura de datos backend.
  - Corrección visual complementaria en UI 2D: barra de llenado por Shelf con semáforo coherente (bajo rojo, medio ámbar, alto verde).

- **Issue #12 - Vista Stores Map (Leaflet full-screen + hover card)**: ✅ Completada
  - Sin cambios de esquema ni nuevas entidades.
  - La vista `stores/map` consume directamente la entidad `Store` y sus atributos ya existentes:
    `id`, `name`, `image`, `location`, `address`, `countryCode`, `temperature`, `relativeHumidity`.
  - `location` (`geo:json Point`) se usa para posicionamiento de marcadores y cálculo de `fitBounds`.
  - `address` (StructuredValue) se renderiza en tarjeta emergente al hover con formateo legible.
  - `countryCode` se usa para bandera visual (ISO alpha-2) en tooltip de mapa.
  - No se altera contrato de API REST de entidades; solo se amplía el contexto enviado por `GET /stores/map` a plantilla.

- **Issue #13 - Integración Orion (providers de contexto)**: ✅ Completada
  - Detección de conectividad Orion consolidada con doble comprobación (`GET /version` + fallback `GET /v2/entities?limit=1`).
  - Selección de backend activa en runtime (`orion` o `sqlite`) con fallback automático.
  - Registro idempotente de providers para `Store` validando previamente `GET /v2/registrations`:
    - attrs `temperature`, `relativeHumidity` -> provider weather (`http://tutorial:3000/random/weatherConditions`)
    - attrs `tweets` -> provider catfacts tweets (`http://tutorial:3000/catfacts/tweets`)
  - Registro por `Store` usando `entities[].id` para compatibilidad con Orion en este entorno.
  - Campo `description` de registration normalizado (`smart-store-...`) para evitar rechazos `400 BadInput`.
  - Se elimina la dependencia de registrations legacy (`queryContext`) para asegurar resolución de attrs de provider en consultas NGSIv2.
  - Contrato de datos de `Store` se mantiene sin cambios de esquema (`temperature`, `relativeHumidity`, `tweets` ya definidos).
  - `stores/detail.html` consume y muestra estos atributos en render de servidor, dejando de ser placeholders.
  - Lectura de `Store` robusta ante fallo de provider: si la consulta con attrs de provider falla, se aplica fallback a lectura base de Orion sin romper la vista.
  - Presentación defensiva en frontend: `N/A` para `temperature`/`relativeHumidity` cuando no hay dato y mensaje explícito cuando `tweets` llega vacío.
  - Endpoints de actualización CRUD en las 5 entidades aceptan tanto `PUT` como `PATCH`.

- **Issue #14 - Suscripciones Orion + realtime Socket.IO**: ✅ Completada
- **Issue #15 - Refinado técnico y mejoras de experiencia de usuario**: ✅ Completada
  - Home simplificada: eliminación del bloque "Estado del Sistema" para reducir complejidad visual
  - Normalización robusta de humedad: dual-format (0..1 decimal y 0..100 porcentaje) con clamping automático
  - Sonda de providers: verificación de accesibilidad de `tutorial:3000` al arranque tras registro
  - Umbral de bajo stock: actualización global de 5 a 10 unidades (config.py, app/__init__.py subscripciones)
  - Integración T/H en card principal: temperatura y humedad incluidas en tarjeta de atributos Store con semáforo dinámico (normal/high/low) según rangos de temperatura/humedad
  - Escena 3D mejorada: tooltip multi-línea con nombre producto, unidades en shelf y stock total; reposicionamiento lateral inteligente con bounds checking
  - Validaciones formularios endurecidas: patterns HTML5 + regex JavaScript para nombres, países, usernames, coordinates; bounds numéricos para precios, salarios, cantidades
  - Map popup compactado: reducción de ancho (260px) e imagen (96px) con padding tighter para evitar recortes en pantallas pequeñas
  - Seed refactorizado: loop bash generador de 64 InventoryItems (16 shelves × 4 productos) garantizando mínimo 4 productos por estantería
  - Operaciones NGSIv2 para suscripciones añadidas al cliente Orion:
    - listado `GET /v2/subscriptions`,
    - alta `POST /v2/subscriptions`.
  - Registro de suscripciones en arranque con idempotencia (sin duplicados):
    - `Product.price` change,
    - `InventoryItem.stockCount` con condición `stockCount < LOW_STOCK_THRESHOLD`.
  - Webhook `POST /notify` amplía el payload de eventos de dominio:
    - `product_price_change`: `productId`, `name`, `price`, `timestamp`.
    - `low_stock`: `inventoryItemId`, `storeId/storeName`, `productId/productName`, `shelfId`, `stockCount`, `threshold`, `timestamp`.
  - Contrato de datos existente no cambia; se añaden únicamente proyecciones/eventos para capa realtime.
  - Frontend mantiene alertas de bajo stock por `storeId` en almacenamiento local para render diferido en detalle de Store.

**Nota**: El modelo está completamente implementado en `app/models/entities.py` con todos los atributos, relaciones y método `to_dict()`. La población de datos se realiza automáticamente mediante el script `import-data` (genera en Orion: 4 stores, 10 products, 4 employees, 16 shelves, 16 inventory items). El acceso CRUD se realiza vía `app/services/entity_service.py` que soporta tanto SQLite como Orion NGSIv2. Los IDs de nuevas entidades siguen el formato `urn:ngsi-ld:<Type>:<uuid4_hex12>`. Las estadísticas de la home se consultan dinámicamente desde el backend activo sin cachés.

## 1. Alcance del modelo

El modelo de datos se implementa en Orion NGSIv2 y cubre cinco entidades: `Store`, `Product`, `Shelf`, `InventoryItem`, `Employee`.

## 2. Convenciones

- Identificadores con formato URN: `urn:ngsi-ld:<Type>:<NNN>`.
- `type` fija el tipo logico de entidad.
- Los valores siguen tipos NGSIv2 (`Text`, `Number`/`Integer`, `DateTime`, `geo:json`, `Relationship`, `Array`).

## 3. Entidades y atributos

## 3.1 Store

Descripcion: unidad fisica de supermercado.

Atributos:

- `id` (String, PK): ej. `urn:ngsi-ld:Store:001`
- `type` (String): `Store`
- `name` (Text)
- `address` (StructuredValue): `streetAddress`, `addressLocality`, `addressRegion`, `postalCode`
- `location` (geo:json Point): coordenadas `[lon, lat]`
- `image` (Text): URL imagen
- `url` (Text)
- `telephone` (Text)
- `countryCode` (Text): ISO 3166-1 alpha-2
- `capacity` (Number)
- `description` (Text)
- `temperature` (Number): provider externo
- `relativeHumidity` (Number): provider externo, rango esperado `0.0-1.0`
- `tweets` (Array): provider externo

## 3.2 Product

Descripcion: producto comercializable.

Atributos:

- `id` (String, PK): ej. `urn:ngsi-ld:Product:001`
- `type` (String): `Product`
- `name` (Text)
- `size` (Text): valores esperados `S`, `M`, `L`, `XL`
- `price` (Number): precio en euros
- `image` (Text): URL imagen
- `originCountry` (Text)
- `color` (Text): RGB hexadecimal, ej. `#FF5733`

## 3.3 Shelf

Descripcion: estanteria dentro de una tienda.

Atributos:

- `id` (String, PK): ej. `urn:ngsi-ld:Shelf:001`
- `type` (String): `Shelf`
- `location` (Text o geo:json segun implementacion): ubicacion interna en tienda
- `name` (Text)
- `maxCapacity` (Number)
- `refStore` (Relationship -> Store.id)

## 3.4 InventoryItem

Descripcion: relacion operacional entre Store, Shelf y Product con cantidades.

Atributos:

- `id` (String, PK): ej. `urn:ngsi-ld:InventoryItem:001`
- `type` (String): `InventoryItem`
- `refStore` (Relationship -> Store.id)
- `refShelf` (Relationship -> Shelf.id)
- `refProduct` (Relationship -> Product.id)
- `stockCount` (Number): unidades totales del producto en la tienda
- `shelfCount` (Number): unidades del producto en esa shelf

## 3.5 Employee

Descripcion: persona empleada en una tienda.

Atributos:

- `id` (String, PK): ej. `urn:ngsi-ld:Employee:001`
- `type` (String): `Employee`
- `name` (Text)
- `image` (Text): URL foto
- `salary` (Number)
- `role` (Text): ej. `Manager`, `Cashier`, `Stock`
- `refStore` (Relationship -> Store.id)
- `email` (Text)
- `dateOfContract` (DateTime)
- `skills` (Array): valores esperados `MachineryDriving`, `WritingReports`, `CustomerRelationships`
- `username` (Text)
- `password` (Text): almacenada como hash

## 4. Relaciones y cardinalidades

- Store 1 -> N Shelf (`Shelf.refStore`).
- Store 1 -> N Employee (`Employee.refStore`).
- Product N <-> N Shelf via InventoryItem.
- Store 1 -> N InventoryItem (`InventoryItem.refStore`).
- Shelf 1 -> N InventoryItem (`InventoryItem.refShelf`).
- Product 1 -> N InventoryItem (`InventoryItem.refProduct`).

## 5. Reglas de integridad

- `refStore`, `refShelf`, `refProduct` deben apuntar a entidades existentes.
- En `InventoryItem`, `refShelf` debe pertenecer al mismo `refStore`.
- `stockCount >= 0` y `shelfCount >= 0`.
- `shelfCount <= maxCapacity` de la `Shelf` asociada.
- `countryCode` debe tener 2 caracteres.
- `color` debe cumplir patron hexadecimal (`^#[0-9A-Fa-f]{6}$`).
- `email` debe tener formato valido.

## 6. Reglas de negocio derivadas

- Evento de bajo stock: cuando `InventoryItem.stockCount` cae por debajo del umbral definido (ej. 5), se genera notificacion.
- Compra de unidad en Store detail: decrementa `shelfCount` y `stockCount` por PATCH sobre el `InventoryItem`.
- Cambio de `Product.price`: debe propagar notificacion y actualizar vistas en tiempo real.

Detalle Issue #14:
- Umbral de bajo stock configurable mediante `LOW_STOCK_THRESHOLD` (default 5).
- Notificaciones recibidas fuera de la vista Store objetivo se conservan localmente hasta que el usuario accede al detalle.

## 7. Datos iniciales esperados

Carga inicial minima:

- 4 Stores.
- 4 Shelfs por Store.
- 4 Employees (al menos 1 por Store).
- 10 Products.
- InventoryItems suficientes para tener al menos 4 Products por Shelf.

## 8. Consultas y operaciones tipicas

- Listado por tipo: `GET /v2/entities?type=Store|Product|Shelf|InventoryItem|Employee`.
- Agrupaciones en UI:
  - Product detail por Store y Shelf.
  - Store detail por Shelf y Product.
- Actualizacion parcial: `PATCH /v2/entities/{id}/attrs` para precio o stock.

## 9. Supuestos y notas

- El tipo exacto de `Shelf.location` puede variar entre texto descriptivo y geo:json segun implementacion final.
- El umbral de bajo stock puede fijarse inicialmente en 5 si no se parametriza.
- Atributos `temperature`, `relativeHumidity` y `tweets` pueden no estar presentes si el provider externo no responde.
