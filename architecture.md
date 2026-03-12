# Architecture - FIWARE Smart Store

## Estado Actual
**Issue #1 - Estructura base completada:**
- Estructura Flask con blueprints listos (aún vacíos)
- Configuración base para SQLite y Orion
- Sistema de detección de backend en arranque
- Scripts de gestión de contenedores (start.sh, stop.sh)
- Inicialización de SQLAlchemy
- Socket.IO configurado pero sin handlers aún

**Issue #2 - Modelos de datos completados:**
- Modelos SQLAlchemy definidos en `app/models/entities.py` para todas las 5 entidades
- Relaciones referentes (FK) entre Store-Shelf, Store-Employee, Store-InventoryItem, Shelf-InventoryItem, Product-InventoryItem
- Flask-Migrate inicializado en `migrations/`
- Script `import-data.py` que crea y carga la BD SQLite con datos de prueba
- Base de datos validada con 4 stores, 16 shelves, 4 employees, 10 products, múltiples inventory items

**Issue #3 - Rutas y API REST completados:**
- Capa de servicio en `app/services/` con cliente NGSIv2 (`orion_client.py`) y CRUD unificado (`entity_service.py`)
- 6 blueprints activos registrados: main_bp, stores_bp, products_bp, employees_bp, shelves_bp, inventory_bp
- 34 rutas registradas (vistas placeholder texto plano + API REST completa para las 5 entidades)
- Filtros dinámicos: `GET /api/shelves?store=<id>&excludeProduct=<id>` y `GET /api/products?excludeShelf=<id>`
- Endpoint `POST /notify` que clasifica notificaciones Orion y emite eventos Socket.IO (`product_price_change`, `low_stock`)
- Manejo global de errores 400/404/405/500 con formato JSON `{"error": {"code": N, "message": "..."}}`
- Backend activo detectable en tiempo de arranque: SQLite (desarrollo) o Orion (producción)

## 1. Resumen

La solucion sigue una arquitectura web cliente-servidor integrada con FIWARE Orion Context Broker (NGSIv2) para gestion de contexto y notificaciones en tiempo real.

## 2. Componentes

### 2.1 Frontend

- HTML/CSS/JavaScript
- Socket.IO client
- Leaflet para mapas
- Three.js para vista 3D
- Mermaid para diagrama UML
- Font Awesome para iconografia

Responsabilidades:

- Render de vistas y tablas.
- Ejecucion de formularios y validaciones cliente.
- Suscripcion a eventos en tiempo real por Socket.IO.

### 2.2 Backend

- Flask
- Flask-SocketIO

Responsabilidades:

- Exponer endpoints HTTP de aplicacion.
- Orquestar operaciones CRUD contra Orion (NGSIv2).
- Registrar providers y suscripciones al arrancar.
- Recibir notificaciones Orion y retransmitir a clientes por WebSocket.

### 2.3 Context Broker

- FIWARE Orion (`fiware-orion`) en puerto 1026.

Responsabilidades:

- Persistir y servir entidades NGSIv2.
- Gestionar registros de proveedores de contexto externos.
- Emitir notificaciones por suscripciones.

### 2.4 Base de datos

- MongoDB (`db-mongo`) en puerto 27017.

Responsabilidades:

- Persistencia para Orion.

### 2.5 Context providers

- `tutorial:3000/proxy/v1/random/weatherConditions` -> `temperature`, `relativeHumidity`
- `tutorial:3000/proxy/v1/catfacts/tweets` -> `tweets`

## 3. Vista de despliegue (Docker Compose)

Servicios principales definidos:

- `orion-v2` (imagen `quay.io/fiware/orion`)
- `tutorial` (imagen `quay.io/fiware/tutorials.context-provider`)
- `mongo-db` (imagen `mongo`)

Red:

- red Docker comun del stack para comunicacion entre contenedores.

Nota:

- El compose es de tutorial, no orientado a produccion.

## 4. Secuencia de arranque

1. Levantar contenedores (`services start` o script equivalente `start.sh`).
2. Esperar Mongo healthy.
3. Crear indices requeridos por Orion en Mongo.
4. Esperar Orion healthy.
5. Ejecutar `import-data` para cargar entidades base y registros iniciales.
6. Iniciar Flask app.
7. Registrar context providers externos en Orion.
8. Registrar suscripciones NGSIv2.
9. Dejar Socket.IO escuchando para clientes web.

## 5. Integracion NGSIv2

### 5.1 Entidades

- Store
- Product
- Shelf
- InventoryItem
- Employee

### 5.2 Operaciones

- Lectura: `GET /v2/entities` (y filtros por tipo/atributos).
- Escritura: `POST /v2/entities` o `POST /v2/op/update`.
- Actualizacion parcial: `PATCH /v2/entities/{id}/attrs`.
- Borrado: `DELETE /v2/entities/{id}`.

### 5.3 Registros de provider

- Registro para `temperature` y `relativeHumidity`.
- Registro para `tweets`.

### 5.4 Suscripciones

- Cambios en `Product.price`.
- Cambios en `InventoryItem.stockCount` por debajo de umbral.

## 6. Flujo de eventos en tiempo real

### 6.1 Cambio de precio

1. Cliente o backend actualiza `price` en Orion.
2. Orion evalua suscripcion y envia notificacion a Flask.
3. Flask transforma y emite evento Socket.IO.
4. Clientes conectados actualizan la UI sin refresco completo.

### 6.2 Bajo stock

1. Accion de compra decrementa `shelfCount` y `stockCount` via PATCH.
2. Orion dispara notificacion al cumplirse condicion de bajo stock.
3. Flask publica evento Socket.IO.
4. Vista Store muestra alerta en panel de notificaciones.

## 7. Red y conectividad

- Orion vive en contenedor y Flask puede correr en host.
- URL de callback en suscripciones Orion debe usar `host.docker.internal` en lugar de `localhost`.
- Si Flask corre contenedorizado en la misma red, se puede usar hostname de servicio.

## 8. Decisiones de frontend

- Preferencia por CSS cuando CSS y JS resuelven el mismo efecto.
- JS orientado a actualizar atributos/estado de elementos existentes.
- Evitar crear grandes bloques HTML dinamicos desde JS.

## 9. Observabilidad y operacion

- Healthchecks de Orion y Mongo en Docker Compose.
- Estado operativo visible con `services` script (`docker ps` + puertos).
- Logs de contenedores para diagnostico de integracion.

## 10. Limitaciones conocidas

- Configuracion de tutorial con puertos expuestos y sin hardening.
- Dependencia de providers externos para ciertos atributos de Store.
- Detalles de autenticacion y autorizacion no definidos en setup.
