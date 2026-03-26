# FIWARE Smart Store

Una aplicación web integral para la gestión de una cadena de supermercados, integrando FIWARE Orion como Context Broker (NGSIv2) con notificaciones en tiempo real, visualización 3D inmersiva y una interfaz multilingüe.

**Repositorio:** https://github.com/angelvilarino/GDEI-P2

## Características Principales

- **CRUD Completo**: Gestión de Stores, Products, Shelves, InventoryItems y Employees
- **Tiempo Real**: Notificaciones en vivo vía Socket.IO (cambios de precio, alertas de bajo stock)
- **Integración FIWARE**: Context Broker Orion (NGSIv2) con providers de contexto externos
- **Visualización 3D**: Recorrido inmersivo con Three.js de la distribución interna de tiendas
- **Mapas Interactivos**: Vista de tiendas con Leaflet y navegación geolocalizada
- **Interfaz Bilingüe**: Soporte completo español/inglés (ES/EN)
- **Modo Dark/Light**: Tema completamente personalizable
- **Validaciones Robustas**: HTML5 + JavaScript para integridad de datos
- **Responsive Design**: Adaptable a dispositivos móviles y de escritorio

## Tecnologías

- **Backend**: Python Flask + Flask-SocketIO
- **Frontend**: HTML5, CSS3, JavaScript vanilla
- **Context Broker**: FIWARE Orion (NGSIv2)
- **Base de Datos**: MongoDB (Orion) / SQLite (fallback)
- **Visualización**: Three.js (3D), Leaflet (mapas), Mermaid (diagramas)
- **Contenedorización**: Docker + Docker Compose
- **CDN**: Font Awesome (iconografía)

## Requisitos Previos

- Docker y Docker Compose instalados
- Python 3.8+ (solo si ejecuta sin contenedores)
- Git (para clonar repositorio)

## Instalación y Ejecución

### 1. Clonar el repositorio

```bash
git clone git@github.com:angelvilarino/GDEI-P2.git
cd GDEI-P2
```

### 2. Levantar servicios con Docker

El proyecto incluye un `docker-compose.yml` que orquesta todos los servicios necesarios, integrado con el script de arranque `start.sh` para una experiencia sin complicaciones:

```bash
./start.sh
```

**El script `start.sh` realiza automáticamente:**
- Descarga/construcción de imágenes Docker necesarias
- Levantamiento de Orion (puerto 1026), MongoDB (puerto 27017) y tutorial provider (puerto 3000)
- Parada de servicios previos si existen
- Carga inicial de datos si Orion está vacío
- Inicialización de Flask en puerto 5000

### 3. Acceder a la aplicación

Una vez que los servicios estén listos, abre tu navegador:

```
http://localhost:5000
```

**Tiempo de arranque típico**: 10-15 segundos desde `./start.sh`

### 4. Detener servicios

```bash
./stop.sh
```

Esto apaga todos los contenedores Docker de forma ordenada sin eliminar datos.

## Uso de la Aplicación

### Navegación Principal

- **Home**: Estadísticas de la aplicación y diagrama UML del modelo de datos
- **Stores**: Listado y gestión de tiendas con temperatura/humedad en tiempo real
- **Products**: Catálogo de productos con distribución por tienda y estantería
- **Employees**: Personal de tiendas con roles y competencias
- **Stores Map**: Visualización geográfica interactiva de todas las tiendas

### Funcionalidades Destacadas

#### Vista Store (Detalle)
- Tabla interactiva de inventario agrupada por estantería
- Escena 3D inmersiva con OrbitControls (orbitar, zoom, paneo)
- Tooltip de producto enriquecido al pasar el ratón sobre 3D
- Compra unitaria de productos (decremento de stock en tiempo real)
- Panel de notificaciones en vivo (cambios de precio, alertas de bajo stock)
- Tweets de la tienda desde proveedores externos

#### Vista Map
- Marcadores personalizados con imagen de cada tienda
- Tarjeta emergente con datos clave al pasar el ratón
- Navegación al detalle de tienda con un click
- Ajuste automático de vista para todas las tiendas visibles

#### Vista Employee (Detalle)
- Acceso al detalle desde cualquier punto de la fila en el listado de empleados
- Vista de atributos completa con estilo homogéneo respecto a Store/Product
- Botones de editar y borrar disponibles en la propia vista detalle
- Rol y skills mostrados con iconografía Font Awesome

#### Validaciones
- Formularios endurecidos con patrones HTML5 y JavaScript
- Validación de rangos numéricos (precios, salarios, cantidades)
- Validación de coordenadas geográficas
- Confirmación antes de operaciones destructivas (borrado)

## Estructura del Proyecto

```
GDEI-P2/
├── app/
│   ├── __init__.py              # Inicialización Flask, registro de providers/suscripciones
│   ├── models/
│   │   └── entities.py          # Entidades Orion/SQLAlchemy
│   ├── routes/                  # Blueprints de rutas
│   │   ├── stores.py
│   │   ├── products.py
│   │   ├── employees.py
│   │   ├── shelves.py
│   │   └── inventory.py
│   ├── services/
│   │   ├── orion_client.py      # Cliente NGSIv2
│   │   └── entity_service.py    # CRUD unificado
│   ├── static/
│   │   ├── css/theme.css        # Sistema de diseño (Light/Dark)
│   │   ├── js/
│   │   │   ├── theme.js         # Toggle Dark/Light
│   │   │   ├── i18n.js          # Internacionalización
│   │   │   └── realtime.js      # Socket.IO client
│   │   └── i18n/
│   │       ├── es.json          # Traducciones español
│   │       └── en.json          # Traducciones inglés
│   └── templates/
│       ├── base.html            # Plantilla base con navbar
│       ├── home.html
│       ├── index.html
│       ├── products/
│       │   ├── list.html
│       │   └── detail.html
│       ├── stores/
│       │   ├── list.html
│       │   ├── detail.html      # Con escena 3D
│       │   └── map.html         # Leaflet full-screen
│       └── employees/
│           └── list.html
├── config.py                    # Configuración (umbral LOW_STOCK_THRESHOLD=10)
├── app.py                       # Punto de entrada Flask
├── docker-compose.yml           # Orquestación de servicios
├── start.sh                     # Script de arranque
├── stop.sh                      # Script de parada
├── import-data                  # Script de carga inicial (genera 64 items: 16 shelves × 4 productos)
├── requirements.txt             # Dependencias Python
├── PRD.md                       # Documento de requisitos del producto
├── architecture.md              # Arquitectura técnica
├── data_model.md                # Modelo de datos
└── README.md                    # Este archivo

```

## Configuración

### Umbral de Bajo Stock

Por defecto, el sistema alerta cuando el stock de un producto en una estantería cae por debajo de **10 unidades**. Para cambiar este valor:

1. Edita `config.py` y modifica `LOW_STOCK_THRESHOLD`
2. Reinicia con `./stop.sh` y `./start.sh`

### Puertos

- **Aplicación Flask**: 5000
- **Orion Context Broker**: 1026
- **MongoDB**: 27017
- **Tutorial Provider**: 3000

### Variables de Entorno

```bash
export FLASK_ENV=development      # development | production
export FLASK_PORT=5000
export ORION_HOST=localhost
export ORION_PORT=1026
```

## Desarrollo

### Instalar dependencias Python locales

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Ejecutar Flask sin Docker

```bash
python app.py
```

**Nota:** Orion debe estar levantado (vía Docker compose o instalación local)

### Ejecutar tests

```bash
python -m pytest tests/
```

## Integración FIWARE

### Context Providers Registrados

Al arrancar, la aplicación registra automáticamente:

- **Weather Provider** (`tutorial:3000/random/weatherConditions`)
  - Atributos: `temperature`, `relativeHumidity`
  - Aplicado a: Todas las entidades Store

- **Tweets Provider** (`tutorial:3000/catfacts/tweets`)
  - Atributo: `tweets`
  - Aplicado a: Todas las entidades Store

### Suscripciones NGSIv2

Se crean dos suscripciones de Orion:

1. **Cambio de Precio**: Se dispara cuando `Product.price` cambia
2. **Bajo Stock**: Se dispara cuando `InventoryItem.stockCount < 10`

Las notificaciones se reciben en `/notify` y se retransmiten a clientes via Socket.IO.

### Normalización de Humedad

El sistema maneja automáticamente dos formatos:
- **Decimal** (0..1): Multiplicado por 100 → porcentaje
- **Porcentaje** (0..100): Se usa directamente

Ambos se normalizan a 0-100% con clamping automático.

## Resolución de Problemas

### Orion no está disponible

**Error**: `Connection refused http://localhost:1026`

**Solución**:
```bash
./start.sh  # Levanta Orion automáticamente
```

### Puerto 5000 en uso

**Error**: `Address already in use`

**Solución**:
```bash
lsof -i :5000
kill -9 <PID>
```

### Cache de navegador anticuado

**Solución**:
- Limpia caché: `Ctrl+Shift+Del` (Windows/Linux) o `Cmd+Shift+Del` (Mac)
- O abre en navegación privada

### Socket.IO desconectado

**Comportamiento normal**: Si el servidor falla, Socket.IO se reconecta automáticamente cada 5 segundos.

## Historial de Cambios

### Issue #15 - Refinado Técnico y Mejoras UX (Última versión)

- ✅ Home simplificada (eliminación del bloque de estado del sistema)
- ✅ Normalización robusta de humedad (dual-format con clamping)
- ✅ Sonda de providers de contexto en arranque
- ✅ Umbral de bajo stock actualizado: 5 → **10 unidades**
- ✅ Integración T/H en card principal de Store con semáforo dinámico
- ✅ Escena 3D: tooltip mejorado (multi-línea, reposicionamiento inteligente)
- ✅ Validaciones formularios endurecidas (patterns, bounds numéricos, regex)
- ✅ Map popup compactado para mejor UX en pantallas pequeñas
- ✅ Seed refactorizado: garantiza 4 productos por estantería
- ✅ Listado de empleados con fila completa navegable a detalle
- ✅ Detalle de empleado con iconos en rol y skills + acciones editar/borrar

### Problemas Conocidos

- El tutorial provider (`tutorial:3000`) puede retardar ocasionalmente la carga de temperatura/humedad. Se aplica fallback automático a `N/A` si la respuesta tarda >5 segundos.

## Contacto y Soporte

Para reportar bugs o sugerencias, abre un issue en GitHub:
https://github.com/angelvilarino/GDEI-P2/issues

## Licencia

Proyecto educativo para la asignatura GDEI (Grado en Desarrollo e Ingeniería).

---

**Última actualización**: 26 de marzo de 2026 | **Issue #15** | **Status**: ✅ Completada + ajustes finales de detalle Employee
