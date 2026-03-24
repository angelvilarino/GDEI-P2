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

**Issue #4 - Layout base, Navbar, i18n y Dark/Light mode completados:**
- `templates/base.html`: plantilla Jinja2 base con navbar sticky (`position: sticky; top: 0`), bloque `{% block content %}` y footer
- Detección de sección activa en navbar: JS puro comparando `window.location.pathname`, sin lógica Flask
- Toggle Dark/Light mode: CSS-first con variables en `:root[data-theme="light"|"dark"]`; `theme.js` escribe atributo y persiste en `localStorage`
- Toggle i18n ES/EN: `i18n.js` carga `/static/i18n/<lang>.json` vía fetch, traduce elementos `data-i18n`, persiste en `localStorage`
- `app/static/css/theme.css`: sistema de diseño completo con variables CSS (colores, sombras, navbar, footer, cards, badges)
- 5 plantillas que extienden base.html: `home.html`, `products/list.html`, `stores/list.html`, `employees/list.html`, `stores/map.html`
- Rutas de vista actualizadas a `render_template()`; nueva ruta `GET /stores/map`; total 35 rutas
- CDN cargados en base.html: Font Awesome 6.5, Leaflet 1.9.4 (CSS+JS), Socket.IO 4.7.5, Mermaid 10

**Issue #5 - Vista Home con estadísticas y diagrama UML completados:**
- Ruta `GET /` (main_bp) genera dinámicamente estadísticas consultando SQLite
- Función `generate_uml_diagram()`: genera diagrama Mermaid ERD mostrando todas las entidades y sus relaciones
- `app/templates/home.html`: 
  - Sección de 4 tarjetas de estadísticas en grid responsive (min 250px)
  - Card para Stores con icono fa-store, color #FF6B6B (rojo)
  - Card para Products con icono fa-box-open, color #4ECDC4 (azul)
  - Card para Employees con icono fa-users, color #95E1D3 (verde)
  - Card para Inventory Items con icono fa-cubes, color #F38181 (rosa)
  - Cada card muestra nombre e ícono con efectos hover (translateY -4px)
  - Sección System Health con verificación de conectividad a Orion
  - Sección Mermaid diagram con diagrama UML renderizado
- Estilos en `theme.css`:
  - `.stats-grid`: grid responsive con gap 1.5rem
  - `.stat-card`: flexbox con gradientes de fondo, sombras, transiciones
  - `.stat-card:hover`: elevación visual con `translateY(-4px)`
  - Colores específicos por tarjeta con tema dark/light
  - `.mermaid-container`: centrado, overflow-x auto, border 1px
- `static/i18n/`: nuevas claves de traducción
  - ES: "Tiendas", "Productos", "Empleados", "Ítems Inventario", "Estado del Sistema", "Diagrama UML"
  - EN: "Stores", "Products", "Employees", "Inventory Items", "System Health", "UML Diagram - Data Model"
- Mermaid integrado en home.html con soporte dinámico para cambio de tema
- Datos verificados con import-data.py: 4 stores, 10 products, 4 employees, 72 inventory items
- Todas las estadísticas se actualizan en cada carga de página desde el backend activo (Orion o SQLite)

**Issue #6 - Integración Orion + carga condicional + vista Products completados:**
- `import-data` convertido a script idempotente de carga NGSIv2 usando `POST /v2/entities` (sin ruta SQLite)
- Dataset inicial cargado en Orion: 4 stores, 16 shelves, 4 employees, 10 products, 16 inventory items
- `start.sh` ahora:
  - espera Orion healthy,
  - consulta `GET /v2/entities?limit=1`,
  - ejecuta `./import-data` solo cuando Orion está vacío
- Home (`GET /`) usa `entity_service` para estadísticas según backend activo (Orion o SQLite)
- `orion_client.py`: lecturas GET con cabecera `Accept` (sin `Content-Type`) para evitar `400 Bad Request` en Orion
- Mermaid renderizado global en `base.html` vía `mermaid.initialize()` + `mermaid.run()` tras DOM y re-render al cambiar tema
- Vista Products implementada con tabla y formulario de alta/edición con validación HTML+JS y confirmación previa al borrado

**Issue #7 - Vista Stores CRUD + consistencia de dataset completados:**
- `start.sh` ahora resetea entidades de Orion y recarga siempre `import-data` para garantizar dataset por defecto tras cada arranque
- Restauración verificada de entidades base tras ciclo `stop.sh` + `start.sh` (incluyendo productos eliminados previamente)
- `app/templates/stores/list.html` implementado con el mismo patrón visual y de interacción que Products:
  - toolbar con botón alta,
  - tabla con acciones editar/borrar,
  - modal de formulario con validaciones HTML+JS,
  - confirmación previa de borrado
- Tabla de Stores enriquecida con:
  - bandera por `countryCode` usando `flagcdn.com`,
  - temperatura y humedad con iconos Font Awesome y semáforo de color por umbrales
- Formulario Store sin `temperature` ni `relativeHumidity` (atributos externos de context provider)
- Fallback de imagen en Stores con Picsum Photos cuando la entidad no tiene imagen
- Carga de imágenes controlada, utilizando fallback visual de Picsum Photos o similares.

**Issue #8 - Vista Employees completada:**
- Formulario de alta/edición adaptado a tipos complejos de NGSIv2.
- Selección de checkbox (skills) consolidada en Array.
- Lógica de formulario interactiva donde la "password" es obligatoria en creación pero opcional y oculta en UI durante edición.
- Select para el Store del empleado con carga asíncrona mediante GET `/api/stores`.
- Interfaz gráfica responsiva reutilizando los estilos y botones core del proyecto.
- Fallback generador de avatares `api.dicebear.com/7.x/personas/svg` usado de manera determinista gracias al nombre del empleado de input.
- Animación interactiva en foto por CSS puramente (`transform: scale()`), según RNF-05 (preferir CSS en vez de JS).

**Issue #9 - Vista detalle de Product completada:**
- Nueva plantilla `products/detail.html` que extiende `base.html` con cabecera hero (imagen, precio, size, originCountry, color hex, botones editar/borrar).
- Tabla de InventoryItems agrupada por Store con filas de cabecera de grupo (total stock, botón añadir a otra Shelf con select dinámico via `GET /api/shelves?store=<id>&excludeProduct=<id>`) y filas de detalle (editar shelfCount inline, borrar ítem), sin recarga de página.
- Si todas las Shelves de un Store ya contienen el producto, se muestra mensaje informativo y el botón confirmar queda deshabilitado.
- `entity_service.py`: `get_inventory_items()` acepta `product_id`; nueva función `get_product_inventory_grouped()` agrupa inventario por Store consultando Orion o SQLite.
- `routes/products.py`: `product_detail()` renderiza `products/detail.html` con producto + inventario agrupado; abort 404 si no existe.
- `routes/inventory.py`: `api_inventory_list()` acepta `?product=<id>` para filtrar por producto.
- `theme.css`: estilos `.inventory-group-header` (borde accent, fondo elevado), `.inventory-detail-row` (indentación), `.product-detail-*`, `.product-name-link`.
- `products/list.html`: nombre de producto enlazado a `/products/<id>`.
- i18n: 20 claves nuevas en ES y EN para toda la vista detalle de producto.

**Issue #10 - Vista detalle de Store (tabla InventoryItems completa):**
- `routes/stores.py`:
  - `GET /stores/<id>` renderiza detalle real de Store,
  - `GET /api/stores/<id>/inventory-grouped` expone agrupación por Shelf para refresco dinámico.
- `entity_service.py`:
  - nueva función `get_store_inventory_grouped(store_id)`,
  - nueva operación `buy_inventory_unit(item_id)` con decremento de `shelfCount` y `stockCount`.
- `routes/inventory.py`: nuevo endpoint `PATCH /api/inventory/<id>/buy` para compra unitaria sin recarga.
- `templates/stores/detail.html`:
  - tabla de InventoryItems agrupada por Shelf (cabecera de grupo + filas de detalle por Product),
  - acciones cliente sin recarga: añadir/editar/borrar InventoryItem, añadir/modificar Shelf, comprar unidad,
  - refresco parcial del bloque mediante fetch al endpoint agrupado.
- `templates/stores/list.html`: fila completa de Store navegable a detalle, manteniendo el enlace explícito en el nombre.
- `theme.css`: estilos para tabla agrupada por Shelf, barra de progreso de llenado y layout responsive de detalle.
- Bloques de `temperature/relativeHumidity`, tweets y notificaciones Socket.IO permanecen marcados como "próximamente" para issue posterior.

**Issue #11 - Recorrido inmersivo 3D (Three.js) en detalle Store:**
- `base.html` incorpora CDN global de Three.js + OrbitControls para reutilización en vistas.
- `templates/stores/detail.html` añade un bloque 3D inmersivo con:
  - escena, cámara y render WebGL no bloqueante,
  - controles de navegación tipo órbita,
  - tooltips en hover por intersección (raycasting),
  - pausa/reanudación de render según visibilidad de pestaña.
- La escena se hidrata directamente con `inventory_groups` generado por backend en la misma carga de plantilla; no se realizan llamadas adicionales para poblar el 3D.
- Modelado visual:
  - suelo y estanterías por Shelf,
  - bloques de producto por ítem de inventario en cada Shelf,
  - etiquetas de texto en escena para `shelfCount` y `stockCount`.
- Adaptación de tema Dark/Light aplicada sobre fondo, materiales e iluminación de la escena 3D.
- Se corrige el semáforo de barra de llenado de Shelf: porcentaje bajo en rojo, medio en ámbar y alto en verde.

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
5. Resetear entidades de Orion para asegurar consistencia del dataset de prácticas.
6. Ejecutar `import-data` para recargar siempre el conjunto por defecto.
7. Iniciar Flask app.
8. Registrar context providers externos en Orion.
9. Registrar suscripciones NGSIv2.
10. Dejar Socket.IO escuchando para clientes web.

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
