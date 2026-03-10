# Data Model - FIWARE Smart Store

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
