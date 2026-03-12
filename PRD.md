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

### Issues Pendientes
- Issue #4 - Plantillas HTML, CSS y frontend completo (Home, Products, Stores, Employees, Map)
- Issue #5 - Integración con Orion y WebSocket (registro de providers, suscripciones)
- Issue #6 - Mapas, 3D y características avanzadas

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
- Store: nombre, url, telefono, countryCode, capacity, description, temperature, relativeHumidity, imagen, location.
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
