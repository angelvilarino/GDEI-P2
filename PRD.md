# PRD - FIWARE Smart Store

## Estado de Implementación

### Issues Completados
- **Issue #1 - Estructura base del proyecto Flask** ✅
  - Estructura de carpetas del proyecto Flask (app, templates, static, tests)
  - app.py con inicialización de Flask y configuración básica
  - config.py con configuración de SQLite y conectividad con Orion
  - database.py con inicialización de SQLAlchemy
  - app/db_or_orion.py para detectar backend activo (Orion o SQLite)
  - Scripts start.sh y stop.sh para gestionar contenedores Docker
  - requirements.txt con todas las dependencias necesarias
  - .gitignore configurado apropiadamente

- **Issue #2 - Modelos de datos y script de importación** ✅
  - Modelos SQLAlchemy para Store, Product, Shelf, InventoryItem, Employee
  - Relaciones bidireccionales y validaciones de integridad
  - Flask-Migrate para gestión de migraciones de BD
  - Script import-data.py que carga 4 stores, 4 shelves/store, 4 employees, 10 products
  - Población automática de InventoryItems (mínimo 4 productos por estantería)
  - Base de datos SQLite funcional y validada

- **Issue #3 - Rutas Flask y API REST** ✅
  - Módulo app/routes/ con un fichero por entidad: stores.py, products.py, employees.py, shelves.py, inventory.py
  - Capa de servicio dual en app/services/: orion_client.py (cliente NGSIv2) y entity_service.py (CRUD unificado)
  - Blueprints activos registrados en app/__init__.py (34 rutas en total)
  - Vistas placeholder texto plano: GET /, /stores, /stores/<id>, /products, /products/<id>, /employees, /employees/<id>
  - API REST CRUD completo (GET list, GET detail, POST, PUT, DELETE) para las 5 entidades
  - Endpoint GET /api/shelves?store=<id>&excludeProduct=<id> para selectores dinámicos
  - Endpoint GET /api/products?excludeShelf=<id> para selectores dinámicos
  - Endpoint POST /notify para notificaciones Orion (price change y low stock) con emisión Socket.IO
  - Manejo global de errores 400/404/405/500 con formato JSON uniforme
  - Todos los endpoints funcionan tanto con SQLite (fallback) como con Orion (cuando disponible)

- **Issue #4 - Layout base, Navbar, i18n y Dark/Light mode** ✅
  - `templates/base.html`: plantilla base con navbar sticky, botones toggle Dark/Light e idioma ES/EN
  - La sección activa de la navbar se resalta vía JS comparando `window.location.pathname` (sin lógica Flask)
  - `app/static/css/theme.css`: variables CSS para temas light/dark (`:root[data-theme]`), estilos CSS-first
  - `app/static/js/theme.js`: aplica `data-theme` en `<html>` antes del primer paint, persiste en `localStorage`
  - `app/static/js/i18n.js`: carga JSON de idioma activo vía fetch, aplica `data-i18n` attrs, persiste en `localStorage`
  - `app/static/i18n/en.json` y `es.json`: todos los textos de UI externalizados (28 claves cada uno)
  - 5 plantillas HTML que extienden base.html: home.html, products/list.html, stores/list.html, employees/list.html, stores/map.html
  - Rutas Flask actualizadas a `render_template()`: /, /stores, /stores/map, /stores/<id>, /products, /products/<id>, /employees, /employees/<id>
  - Nueva ruta `GET /stores/map` añadida (35 rutas totales)
  - CDN incluidos en base.html: Font Awesome 6.5, Leaflet 1.9.4, Socket.IO 4.7.5, Mermaid 10

- **Issue #5 - Vista Home con estadísticas y diagrama UML** ✅
  - Panel de estadísticas en home.html con 4 tarjetas (Stores, Products, Employees, Inventory Items)
  - Tarjetas con iconos Font Awesome, colores degradados y efectos hover
  - Estadísticas consultadas dinámicamente desde SQLite: counts de cada entidad
  - Diagrama UML de entidades (Store, Product, Shelf, InventoryItem, Employee) generado con Mermaid
  - Relaciones entre entidades mostradas en diagrama (1->N, N->N)
  - Soporte completo para temas Dark/Light: estilos adaptados dinámicamente
  - Mermaid se re-renderiza al cambiar de tema
  - Datos verificados con import-data.py: 4 stores, 10 products, 4 employees, 72 inventory items
  - Internacionalización (ES/EN) para todas las nuevas etiquetas

- **Issue #6 - Integración Orion + carga condicional + vista Products** ✅
  - Script `import-data` migrado a carga directa de Orion con `POST /v2/entities` (NGSIv2), sin SQLite
  - `start.sh` ejecuta carga condicional: solo corre `import-data` si Orion no tiene entidades
  - Home obtiene estadísticas desde backend activo (Orion/SQLite) vía `entity_service`
  - Vista Products implementada en `products/list.html` con:
    - botón de alta,
    - tabla (imagen, nombre, color, size, originCountry),
    - acciones editar/borrar,
    - formulario alta/edición con inputs variados (`text`, `number`, `color`, `select`, `file`, `url`, `date`, `checkbox`, `radio`),
    - validación HTML + JS y confirmación en borrado
  - Clave i18n `page_home_orion_error` corregida con texto descriptivo en ES/EN
  - Mermaid centralizado en `base.html` con `mermaid.initialize()` y `mermaid.run()` tras carga de DOM

- **Issue #7 - Vista Stores CRUD + consistencia de dataset por defecto** ✅
  - `start.sh` ahora restablece entidades de Orion y recarga siempre `import-data` en cada arranque
  - Garantizada la restauración del dataset por defecto tras `./stop.sh` + `./start.sh` (incluye Products)
  - Vista `stores/list.html` implementada con patrón visual/estructura de Products (toolbar, tabla, modal, botones)
  - Tabla Stores con columnas: imagen, nombre, `countryCode` con bandera (`flagcdn`), temperatura y humedad con iconos/colores por umbral, acciones editar/borrar
  - Formulario alta/edición de Store con inputs variados (`text`, `url`, `tel`, `number`, `range`, `textarea`) y validación HTML + JS
  - `temperature` y `relativeHumidity` excluidos del formulario (atributos externos de context provider)
  - Confirmación obligatoria antes de borrar Store
  - Fallback de imagen de Store con Picsum Photos cuando no existe imagen propia
  - Nuevas claves de traducción ES/EN añadidas para toda la vista Stores
  - Toggle Dark/Light, toggle de idioma y resaltado navbar validados en la vista Stores

- **Issue #8 - Mapas, 3D y características avanzadas (Vista Employees completada)** ✅
  - Vista `employees/list.html` implementada con el mismo patrón visual (table, toolbar, modal).
  - Foto con transición CSS zoom al pasar el ratón (`transform: scale(1.2)`).
  - Rol representado con iconos y badge (`Manager`: corbata, `Cashier`: caja, `Stock`: caja).
  - Habilidades múltiples (skills) en formato badge con iconos específicos.
  - CRUD con validación HTML y JS (fechas, contraseñas, URLs).
  - Fallback de DiceBear para la foto del empleado en caso de usar imagen vacía.
  - Peticiones PUT y POST adaptadas a las reglas NGSIv2 para esta entidad.
  - Traducciones completadas (ES/EN) para todos los campos.

- **Issue #9 - Vista detalle de Product con tabla de inventario agrupada por Store** ✅
  - Vista `products/detail.html` con cabecera hero: imagen (fallback PRODUCT_IMAGES), nombre, precio €, size, originCountry, cuadrado de color hex, botón Editar (modal reutilizado del form de lista) y botón Borrar con confirmación
  - Tabla de InventoryItems agrupada por Store con dos niveles de fila:
    - Fila de cabecera de grupo (`inventory-group-header`): icono + bandera + nombre Store + badge total stock + botón "Añadir a otra Shelf" con panel inline que carga dinámicamente via `GET /api/shelves?store=<id>&excludeProduct=<id>` las Shelves disponibles; si no hay Shelves disponibles se muestra mensaje informativo y el botón confirmar queda deshabilitado
    - Filas de detalle (`inventory-detail-row`): nombre Shelf + badge shelfCount + botón editar shelfCount inline (PUT `/api/inventory/<id>`) + botón borrar ítem (DELETE + confirm)
  - Todos los cambios actualizan la tabla sin recargar la página entera
  - `products/list.html`: nombre de producto enlazado a `/products/<id>`
  - `entity_service.py`: `get_inventory_items()` acepta `product_id`; nueva función `get_product_inventory_grouped()`
  - `routes/products.py`: `product_detail()` pasa producto + inventario agrupado a la plantilla; `abort(404)` si no existe
  - `routes/inventory.py`: endpoint acepta `?product=<id>`
  - Estilos en `theme.css`: `.inventory-group-header`, `.inventory-detail-row`, `.product-detail-*`, `.product-name-link`
  - 20 claves nuevas de i18n en ES/EN para toda la vista detalle

- **Issue #10 - Vista detalle Store (InventoryItems y Shelves)** ✅
  - Ruta `GET /stores/<id>` activada para renderizar `stores/detail.html` con datos reales de Store (404 si no existe)
  - `entity_service.py`: nueva función `get_store_inventory_grouped(store_id)` que devuelve inventario agrupado por Shelf con detalle de Product
  - Tabla InventoryItems por Shelf implementada en `stores/detail.html` con dos niveles de fila:
    - cabecera por Shelf con nombre, ubicación, barra de progreso de llenado y acciones
    - detalle por Product con imagen, nombre, precio, size, color, stockCount, shelfCount y acciones
  - Acción "Comprar unidad" implementada sin recarga completa mediante `PATCH /api/inventory/<id>/buy` (decrementa `shelfCount` y `stockCount`)
  - Acciones de tabla sin recarga completa: añadir/editar/borrar InventoryItem y añadir/modificar Shelf
  - API adicional `GET /api/stores/<id>/inventory-grouped` para refresco dinámico del bloque de tabla
  - Cabecera visual del Store mantenida (imagen hover zoom+rotación, datos principales, mapa Leaflet)
  - `stores/list.html`: toda la fila de cada Store es clicable hacia detalle (`/stores/<id>`) y el nombre también queda enlazado
  - Secciones de `temperature/relativeHumidity`, tweets y notificaciones en tiempo real quedan preparadas para issue posterior
  - Nuevas claves i18n en `es.json` y `en.json` para textos de detalle Store

- **Issue #11 - Recorrido inmersivo 3D en detalle Store (Three.js)** ✅
  - `stores/detail.html` incorpora una nueva sección de recorrido inmersivo 3D integrada en el layout de detalle
  - La escena 3D se construye exclusivamente con `inventory_groups` ya embebido en plantilla (sin peticiones adicionales al backend)
  - Representación visual del interior de tienda con estanterías (Shelves) y productos por Shelf, adaptada a número real de Shelves/Items/cantidades
  - Etiquetas visibles en escena por producto con `shelfCount` y `stockCount` mediante sprites de texto
  - Navegación de cámara implementada con `OrbitControls` (orbitar, zoom, paneo)
  - Contenedor 3D responsive con tooltip de producto y comportamiento no bloqueante (pausa del render al ocultar pestaña)
  - Soporte Dark/Light aplicado a fondo, iluminación y materiales de la escena
  - Corregido semáforo de barra de llenado por Shelf: bajo rojo, medio ámbar, alto verde
  - Nuevas claves i18n ES/EN añadidas para título, ayuda y tooltips del módulo 3D
  - Mejora estética de escena para simular supermercado real:
    - layout por pasillos (aisles) con circulación despejada,
    - estanterías modeladas con marcos laterales y baldas horizontales,
    - productos representados como grupos de objetos sobre baldas (no bloques simples),
    - colores diferenciados por categoría de producto,
    - suelo texturizado tipo baldosa/hormigón pulido,
    - iluminación ambiental + focos tipo fluorescente en techo,
    - etiquetas nítidas de stock e ID con CSS2DRenderer.

- **Issue #12 - Vista Stores Map (Leaflet full screen + navegación)** ✅
  - Ruta `GET /stores/map` actualizada para pasar a plantilla la lista completa de Stores
  - Vista `stores/map.html` implementada con mapa Leaflet en formato pantalla completa dentro del layout
  - Marcadores personalizados por tienda con imagen superpuesta (Leaflet `L.divIcon`)
  - Tarjeta emergente al hover por tienda con imagen, nombre, dirección, bandera por `countryCode`, temperatura y humedad con iconos
  - Navegación al detalle de Store en click sobre marcador (`/stores/<id>`)
  - Ajuste automático de centro/zoom para todas las tiendas visibles mediante `fitBounds`
  - Fallback de mensaje cuando no existen tiendas con coordenadas válidas
  - Soporte Dark/Light con tiles de mapa adaptados dinámicamente al tema activo
  - Claves i18n nuevas añadidas en ES/EN para mensajes específicos del mapa
  - Resaltado de navbar corregido para activar solo la ruta más específica (`/stores/map` frente a `/stores`)

- **Issue #13 - Integración con Orion (providers de contexto)** ✅
  - Detección de conectividad Orion consolidada al arranque con healthcheck principal `GET /version` y fallback `GET /v2/entities?limit=1`
  - Selección de backend activo robusta: Orion cuando hay conectividad, SQLite como fallback
  - Registro idempotente de context providers en arranque (sin duplicados, validando `GET /v2/registrations`):
    - `temperature` + `relativeHumidity` para `Store` -> `tutorial:3000/proxy/v1/random/weatherConditions`
    - `tweets` para `Store` -> `tutorial:3000/proxy/v1/catfacts/tweets`
  - Endpoints CRUD de las 5 entidades alineados para actualización por `PUT/PATCH`
  - Vista `stores/detail.html` actualizada para mostrar datos reales de temperatura, humedad y tweets
  - `start.sh` actualizado para parar contenedores previos antes de volver a levantarlos

### Issues Pendientes
- Panel de notificaciones en tiempo real del detalle de Store (Socket.IO), con UX final integrada.

## 1. Contexto

FIWARE Smart Store es una aplicacion web para gestion de una cadena de supermercados. La solucion usa Flask + FIWARE Orion (NGSIv2) y debe actualizar la interfaz en tiempo real usando WebSocket cuando Orion emite notificaciones.

## 2. Objetivo del producto

Entregar una aplicacion que permita gestionar Stores, Products, Shelfs, InventoryItems y Employees, con:

- operaciones CRUD,
- visualizacion de informacion operativa,
- integracion con proveedores de contexto externos,
- notificaciones de cambios en tiempo real,
- interfaz bilingue (ES/EN) y modo Dark/Light.

## 3. Alcance

Incluido en alcance:

- Backend con Flask y Flask-SocketIO.
- Frontend HTML/CSS/JS + Socket.IO.
- Integracion NGSIv2 con Orion.
- Registro de context providers y suscripciones en arranque.
- Formularios con validacion HTML + JS.
- Vistas: Home, Products, Stores, Employees, Stores Map.

Fuera de alcance:

- Hardening productivo del entorno Docker de tutorial.
- Escalado multi-nodo.
- Seguridad enterprise (TLS, IAM corporativo, etc.) mas alla de lo pedido.

## 4. Stakeholders

- Equipo de desarrollo.
- Docente/evaluador de la practica.
- Usuario operador de la aplicacion (gestion de tienda).

## 5. Requisitos funcionales

### RF-01 Gestion de entidades

El sistema debe permitir CRUD de:

- Store
- Product
- Shelf
- InventoryItem
- Employee

### RF-02 Vista Home

La vista Home debe mostrar:

- total de stores,
- total de products,
- total de employees,
- total de inventory items,
- diagrama UML de entidades renderizado con Mermaid.

### RF-03 Vista Products (lista)

La vista Products debe incluir:

- tabla de productos,
- columnas: imagen, nombre, color, size, originCountry,
- acciones: editar, borrar,
- boton para crear Product.

### RF-04 Vista Product (detalle)

Debe mostrar informacion completa del producto y tabla de InventoryItems agrupada por Store:

- cabecera por Store con stockCount total,
- detalle por Shelf con shelfCount,
- accion para anadir InventoryItem en Shelf del Store que no tenga ese Product.

### RF-05 Vista Stores (lista)

La vista Stores debe incluir:

- tabla de tiendas,
- columnas: imagen, nombre, countryCode, temperature, relativeHumidity,
- acciones: editar, borrar,
- boton para crear Store.

### RF-06 Vista Store (detalle)

Debe incluir:

- datos completos de Store,
- mapa Leaflet con ubicacion,
- foto con transicion CSS y animacion de rotacion 360,
- temperatura/humedad con iconos y colores,
- vista 3D inmersiva de la tienda con Three.js,
- tabla de InventoryItems agrupada por Shelf,
- barra de progreso de llenado por Shelf (verde/amarillo/rojo),
- accion comprar unidad (decrementa shelfCount y stockCount por PATCH a Orion),
- accion modificar Shelf,
- accion anadir InventoryItem por Product no presente,
- accion anadir Shelf,
- tweets de la tienda,
- panel de notificaciones en tiempo real.

### RF-07 Vista Employees (lista)

Debe incluir:

- tabla de empleados,
- columnas: foto, nombre, role, skills,
- transicion CSS zoom en foto,
- iconos por role y skills,
- acciones: editar, borrar,
- boton para crear Employee.

### RF-08 Vista Stores Map

Debe incluir:

- mapa Leaflet a pantalla completa,
- marcador por cada Store,
- imagen superpuesta en marcador,
- tarjeta emergente al hover,
- navegacion a detalle Store al click.

### RF-09 Integracion con context providers

Al arrancar, la aplicacion debe registrar en Orion:

- provider de temperature y relativeHumidity,
- provider de tweets,
ambos para entidades Store.

### RF-10 Suscripciones NGSIv2

Al arrancar, la aplicacion debe crear suscripciones:

- cambio de price en Product,
- stockCount de InventoryItem por debajo de umbral (ejemplo: 5).

### RF-11 Notificaciones en tiempo real

Cuando Flask reciba una notificacion Orion:

- debe reenviarla por Socket.IO,
- debe actualizar UI sin refresco completo,
- cambios de price deben reflejarse en todas las vistas afectadas,
- eventos de bajo stock deben mostrarse en panel de Store.

### RF-12 Carga inicial de datos

Debe existir script `import-data` que cargue como minimo:

- 4 Stores,
- 4 Shelfs por Store,
- 4 Employees (>=1 por Store),
- 10 Products,
- InventoryItems suficientes para >=4 Products por Shelf.

## 6. Requisitos no funcionales

- RNF-01 Bilingue ES/EN con toggle.
- RNF-02 Dark/Light mode con toggle.
- RNF-03 Responsive en desktop y mobile.
- RNF-04 Actualizacion en tiempo real via WebSocket (sin polling continuo).
- RNF-05 Priorizar CSS frente a JS cuando ambos resuelven la necesidad visual.
- RNF-06 Minimizar generacion dinamica de HTML desde JS; preferir actualizacion de elementos existentes.
- RNF-07 Validacion de formularios por HTML y JS antes de envio.

## 7. Reglas de formularios

- Usar variedad de tipos de input (`text`, `number`, `email`, `date`, `color`, `range`, `checkbox`, `radio`, `select`, `file`, etc.).
- Incluir `required`, `min`, `max`, `pattern` cuando aplique.
- Employee: nombre, email, fecha contratacion, salario, role, refStore, skills, imagen, username, password.
- Store: nombre, url, telefono, countryCode, capacity, description, imagen, location.
  - `temperature` y `relativeHumidity` se reciben de proveedor de contexto externo y no se editan en el formulario.
- Product: nombre, price, size, color, originCountry, imagen.

## 8. Criterios de aceptacion

- CA-01 Al ejecutar el flujo de arranque, Orion y Mongo quedan operativos y se carga data inicial.
- CA-02 Las 5 vistas existen y muestran la informacion esperada.
- CA-03 CRUD de las 5 entidades funciona correctamente.
- CA-04 Cambiar `price` en Orion dispara actualizacion inmediata en UI.
- CA-05 Reducir `stockCount` por debajo del umbral dispara notificacion en Store.
- CA-06 Mapa de Stores permite navegar al detalle con click.
- CA-07 Home muestra metricas y diagrama UML con Mermaid.
- CA-08 Se puede alternar idioma y tema visual.
- CA-09 Formularios bloquean envio de datos invalidos.

## 9. Riesgos y supuestos

Riesgos:

- Configuracion de red Docker/localhost puede romper callbacks de Orion.
- Dependencia de recursos externos (providers, imagenes URL).

Supuestos:

- El puerto de Flask no esta fijado en `setup.md`; se definira en implementacion.
- El umbral de bajo stock se usara inicialmente en 5 si no se parametriza.
- `password` de Employee se almacena con hash (no en texto plano).
