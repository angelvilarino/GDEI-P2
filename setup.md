# Aplicación FIWARE Smart Store mejorada

## Práctica 2 – Gestión de Datos en Entornos Inteligentes

### Objetivo

Construir una aplicación web de gestión de una cadena de supermercados usando Flask (Python) como framework web, integrada con FIWARE Orion Context Broker mediante NGSIv2. La aplicación incluirá registros y suscripciones NGSIv2, envío de notificaciones en tiempo real desde el servidor a la interfaz web, y seguirá el flujo de trabajo GitHub Flow.

---

### Stack tecnológico

- **Backend**: Python, Flask, Flask-SocketIO
- **Frontend**: HTML, CSS, JavaScript, Socket.IO
- **Base de datos**: FIWARE Orion Context Broker (NGSIv2)
- **Contenedores**: Docker, Docker Compose
- **Mapas**: Leaflet JS
- **3D**: Three.js
- **Iconos**: Font Awesome
- **Diagramas**: Mermaid

---

### Flujo de trabajo GitHub Flow

Cada actuación de implementación se debe llevar hacer usando el flujo de trabajo **GitHub Flow**:

1. Con el agente en **modo Plan, elaboramos un plan de implementación** del issue que queremos implementar. Cuando lo tengamos finalizado, cambiamos a modo Agente
2. Pedimos al agente que **cree un issue** en el repo remoto GitHub con el contenido del plan.
3. Pedimos al agente que **cree una rama (branch) git** para llevar a cabo la implementación del issue
4. Pedimos al agente que **confirme cambios (commit) en local y suba (push) la nueva rama** al repo remoto.
5. Finalmente, pedimos al agente que **cierre el issue fusionando (merge) la nueva rama a la rama main y que sincronice (push)** con origin/main. Si no somos los propietarios del repo remoto, le pediremos que cree una PR (Pull Request) con la nueva rama. El propietario del repo remoto deberá revisar la PR y fusionarla con main para cerrar el issue.
6. **Actualizar PRD.md, architecture.md y data_model.md siempre después de finalizar la implementación de un issue**.

Este último paso (actualizar los tres archivos md) está indicado en `AGENTS.md` para que el agente no lo omita nunca.

---

### Modelo de datos ampliado

El modelo de datos sigue la especificación del tutorial FIWARE NGSIv2 CRUD Operations, ampliado con los atributos descritos a continuación.

#### Entidad: Store

| Atributo | Tipo | Descripción |
| --- | --- | --- |
| id | String | Identificador único (ej. `urn:ngsi-ld:Store:001`) |
| type | String | Siempre `"Store"` |
| name | Text | Nombre de la tienda |
| address | StructuredValue | Dirección postal (streetAddress, addressLocality, addressRegion) |
| location | geo:json | Coordenadas geográficas (Point) |
| image | Text | URL de la imagen de la tienda |
| url | Text | URL del sitio web de la tienda |
| telephone | Text | Teléfono de contacto |
| countryCode | Text | Código de país ISO 3166-1 alpha-2 (2 caracteres, ej. `"ES"`) |
| capacity | Number | Capacidad en metros cúbicos |
| description | Text | Descripción amplia de la tienda |
| temperature | Number | Temperatura interior (proporcionada por proveedor externo) |
| relativeHumidity | Number | Humedad relativa interior 0.0–1.0 (proporcionada por proveedor externo) |
| tweets | Array | Tweets recientes asociados a la tienda (proporcionados por proveedor externo) |

#### Entidad: Product

| Atributo | Tipo | Descripción |
| --- | --- | --- |
| id | String | Identificador único (ej. `urn:ngsi-ld:Product:001`) |
| type | String | Siempre `"Product"` |
| name | Text | Nombre del producto |
| size | Text | Talla o tamaño (`"S"`, `"M"`, `"L"`, `"XL"`) |
| price | Number | Precio en euros |
| image | Text | URL de la imagen del producto |
| originCountry | Text | País de origen del producto |
| color | Text | Color RGB en hexadecimal (ej. `"#FF5733"`) |

#### Entidad: Shelf

| Atributo | Tipo | Descripción |
| --- | --- | --- |
| id | String | Identificador único (ej. `urn:ngsi-ld:Shelf:001`) |
| type | String | Siempre `"Shelf"` |
| location | Text | Ubicación dentro de la tienda (ej. `"Pasillo 3, Estantería 2"`) |
| name | Text | Nombre o código de la estantería |
| maxCapacity | Number | Capacidad máxima en unidades |
| refStore | Relationship | Referencia al Store al que pertenece |

#### Entidad: InventoryItem

| Atributo | Tipo | Descripción |
| --- | --- | --- |
| id | String | Identificador único (ej. `urn:ngsi-ld:InventoryItem:001`) |
| type | String | Siempre `"InventoryItem"` |
| refStore | Relationship | Referencia al Store |
| refShelf | Relationship | Referencia a la Shelf |
| refProduct | Relationship | Referencia al Product |
| stockCount | Number | Total de unidades en stock en la tienda |
| shelfCount | Number | Unidades en esa estantería concreta |

#### Entidad: Employee

| Atributo | Tipo | Descripción |
| --- | --- | --- |
| id | String | Identificador único (ej. `urn:ngsi-ld:Employee:001`) |
| type | String | Siempre `"Employee"` |
| name | Text | Nombre completo |
| image | Text | URL de la foto del empleado |
| salary | Number | Salario en euros |
| role | Text | Rol en la empresa (ej. `"Manager"`, `"Cashier"`, `"Stock"`) |
| refStore | Relationship | Referencia al Store donde trabaja (cada empleado trabaja en un solo Store) |
| email | Text | Correo electrónico |
| dateOfContract | DateTime | Fecha de contratación |
| skills | Array | Lista de habilidades: valores posibles `"MachineryDriving"`, `"WritingReports"`, `"CustomerRelationships"` |
| username | Text | Nombre de usuario para login |
| password | Text | Contraseña (almacenada con hash) |

### Diagrama UML de entidades (Mermaid)

Crear el diagrama de entidades UML usando Mermaid y mostrarlo renderizado en el apartado Home de la aplicación.

---

### Script de carga de datos inicial

Crear un script `import-data` (tomando como base el del tutorial FIWARE NGSIv2 Subscriptions) que cargue:

- **4 tiendas**, cada una con **4 estanterías**
- **4 empleados** (al menos uno por tienda)
- **10 productos**
- Tantos **InventoryItems** como sean necesarios para que haya **al menos 4 productos por estantería**

Las imágenes de tiendas, productos y empleados deben ser URLs de imágenes gratuitas disponibles en internet o generadas mediante un modelo de imagen. Se debe asegurar que las imágenes usadas para cada entidad sean coherentes (ej. empleados con fotos de personas, productos con fotos de productos, tiendas con fotos de edificios comerciales).

---

### Integración con Orion Context Broker

#### Conectividad

Al arrancar, la aplicación debe asegurarse que hay conectividad con Orion.

#### Docker Compose

La carpeta de la aplicación incluirá el fichero `docker-compose.yml` del tutorial FIWARE NGSIv2 Subscriptions. Se crearán dos scripts:

- `start.sh`: Para el entorno antes de levantarlo, levanta los contenedores Docker, el import-data y arranca la aplicación Flask.
- `stop.sh`: Para todos los contenedores y la aplicación.

#### Proveedores de contexto externo

Al arrancar la aplicación, se registrarán en Orion dos proveedores de contexto externos (la aplicación que corre en el contenedor `tutorial` del tutorial Context Providers):

1. **Proveedor 1**: Proporciona `temperature` y `relativeHumidity` para entidades de tipo Store.
2. **Proveedor 2**: Proporciona `tweets` para entidades de tipo Store.

#### Suscripciones a Orion

Al arrancar la aplicación, se darán de alta en Orion las siguientes suscripciones (siguiendo el tutorial NGSIv2 Subscriptions):

1. **Cambio de precio de un Product**: notificación cuando cambia el atributo `price` de cualquier Product.
2. **Bajo stock de un Product en un Store**: notificación cuando `stockCount` de un InventoryItem cae por debajo de un umbral (ej. 5 unidades).

Como la aplicación escucha en `localhost` pero Orion corre en un contenedor Docker, las URLs de notificación deben usar `host.docker.internal` en lugar de `localhost`.

#### Notificaciones servidor → cliente (WebSocket)

Cuando la aplicación Flask reciba una notificación de Orion, la retransmitirá al navegador usando **Flask-SocketIO** (servidor) y **Socket.IO** (cliente). Los elementos de la UI afectados se actualizarán en tiempo real:

- Cambio de precio: actualizar el precio en todas las vistas donde aparezca ese producto.
- Bajo stock: mostrar la notificación en el panel de notificaciones de la vista Store correspondiente.

---

### Formularios de entrada de datos

- Usar el **mayor número posible de tipos de elemento `<input>`** distintos (text, number, email, date, color, range, checkbox, radio, select, file, etc.).
- Incluir **validación HTML** (atributos `required`, `min`, `max`, `pattern`, etc.) y **validación JS** adicional antes del envío.
- Los formularios de Employee incluirán: text (nombre), email, date (dateOfContract), number (salary), select (role, refStore), checkboxes (skills), file (imagen), text (username), password.
- Los formularios de Store incluirán: text (nombre), url, tel, text (countryCode), number (capacity), textarea (description), number/range (temperature, relativeHumidity), file (imagen), coordenadas (location).
- Los formularios de Product incluirán: text (nombre), number (price), select (size), color (color), text (originCountry), file (imagen).

---

### Principios de implementación frontend

- Cuando algo se pueda hacer tanto con CSS como con JS, **usar CSS**.
- Evitar al máximo generar HTML desde JS. El código JS debe **actualizar atributos de elementos HTML ya existentes** en lugar de crear nuevos elementos dinámicamente.
- Consultar la sección HowTo de W3Schools para implementar efectos visuales.

---

### Estructura de la interfaz

La interfaz soporta **inglés y castellano** (toggle de idioma) y tiene **modo Dark y Light** (toggle).

#### Barra de navegación

- Secciones: **Home / Products / Stores / Employees / Stores Map**
- La sección activa debe estar resaltada visualmente.
- La barra permanece visible al hacer scroll.

#### Vista Home

- Resumen con estadísticas generales: número de tiendas, productos, empleados, ítems de inventario.
- Diagrama UML de entidades renderizado con Mermaid.

#### Vista Products (lista)

- Tabla con todas las entidades Product.
- Columnas: imagen, nombre, `color` (cuadrado del color), `size`, `originCountry`, botón editar, botón borrar.
- Botón al inicio de la vista para **añadir un nuevo Product**.

#### Vista detalle Product

- Información completa del producto.
- Tabla de InventoryItems agrupada por Store:
  - Fila de cabecera de grupo: nombre del Store + `stockCount` total para ese producto.
  - Filas de detalle: `shelfCount` para cada Shelf que contiene ese Product.
  - En cada cabecera de grupo Store: botón para **añadir un InventoryItem** con ese Product en otra Shelf de ese Store. El selector de Shelf cargará dinámicamente solo las Shelfs de ese Store que todavía no contengan ese Product.

#### Vista Stores (lista)

- Tabla con todas las entidades Store.
- Columnas: imagen, nombre, `countryCode` (con icono de bandera), `temperature` (con icono y color), `relativeHumidity` (con icono y color), botón editar, botón borrar.
- Botón al inicio de la vista para **añadir un nuevo Store**.

#### Vista detalle Store

- Información completa de la tienda.
- **Mapa Leaflet JS** con la ubicación de la tienda.
- **Foto del almacén** con transición CSS que amplíe la foto y animación CSS de rotación 360°.
- **Temperatura y humedad relativa** con iconos y colores distintos según los valores (ej. rojo para temperatura alta, azul para baja).
- **Recorrido inmersivo virtual 3D** por la tienda usando **Three.js**, mostrando sus estanterías con los productos almacenados, el número de unidades en cada estantería y el total en stock.
- **Tabla de InventoryItems agrupada por Shelf**:
  - Fila de cabecera de grupo: nombre de la Shelf + barra de progreso del nivel de llenado (colores distintos según nivel: verde/amarillo/rojo).
  - Filas de detalle: `image`, `name`, `price`, `size`, `color`, `stockCount`, `shelfCount` de cada Product.
  - En cada fila de InventoryItem: botón para **comprar una unidad** (decrementa `shelfCount` y `stockCount` en Orion mediante `PATCH /v2/entities/<id>/attrs` con `{"$inc": -1}`).
  - En cada cabecera de grupo Shelf: botón para **modificar esa Shelf** y botón para **añadir un InventoryItem** de otro Product no presente en esa Shelf (selector dinámico de Products).
  - Botón para **añadir una nueva Shelf** a ese Store.
- **Tweets del Store** tras la tabla de InventoryItems (icono estilo X/Twitter a la izquierda de cada tweet).
- **Panel de notificaciones** donde se muestran las notificaciones recibidas en tiempo real (ej. stock bajo).

#### Vista Employees (lista)

- Tabla con todas las entidades Employee.
- Columnas: foto (con transición CSS de zoom al pasar el ratón), nombre, `role` (con icono según categoría), `skills` (con iconos por valor), botón editar, botón borrar.
- Botón al inicio de la vista para **añadir un nuevo Employee**.

#### Vista Stores Map

- Mapa Leaflet JS a pantalla completa con la posición de cada Store.
- Imagen del Store superpuesta sobre su marcador en el mapa.
- Al pasar el ratón sobre un Store: tarjeta emergente con imagen y atributos principales.
- Al pulsar sobre un Store: navegar a su vista de detalle.

---

### Aspectos visuales

1. **Vista Employee**: foto con transición CSS de zoom al pasar el ratón.
2. **Vista Store**: foto con transición CSS de zoom + animación CSS de rotación 360°.
3. **Barra de progreso de Shelf**: colores distintos según nivel de llenado (verde < 50%, amarillo 50–80%, rojo > 80%).
4. **Iconos Font Awesome** para compactar la información en tablas:
   - `color`: cuadrado del color correspondiente.
   - `countryCode`: icono con la bandera del país.
   - `role` / `category`: icono distinto según el valor.
   - `skills`: icono distinto por cada habilidad.
   - `temperature`: icono de termómetro con color según valor.
   - `relativeHumidity`: icono de gota con color según valor.
5. **Navbar**: sección activa resaltada, sticky al hacer scroll.
6. **Pestaña Stores Map**: mapa Leaflet con tarjetas emergentes al hover y navegación al detalle al pulsar.
