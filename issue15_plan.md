## Objetivo
Refinado técnico y mejoras de experiencia de usuario para la práctica P2, abarcando Home, Orion Providers, suscripciones de stock, detalle de tienda, escena 3D, validaciones de formularios, mapa de tiendas, seed de inventario y documentación final.

## Alcance y tareas
1. **Home**
   - Eliminar el apartado "Estado del Sistema" de la vista Inicio para simplificar la interfaz.

2. **Orion Providers (temperatura/humedad)**
   - Investigar y corregir el cálculo/render de `relativeHumidity` para evitar valores incoherentes (>1000%).
   - Verificar conectividad con el provider del contenedor `tutorial:3000`.
   - Asegurar mapeo correcto backend/frontend de los atributos de contexto.

3. **Suscripciones bajo stock**
   - Cambiar regla de negocio: notificar bajo stock cuando `stockCount < 10` (antes `< 5`).

4. **Detalle de tienda**
   - Integrar Temperatura y Humedad en la tarjeta principal de atributos.
   - Aplicar colores dinámicos por rango (normal/alerta/extremo).

5. **Escena 3D (Three.js)**
   - En hover de producto mostrar: nombre, unidades en esa estantería y stock total.
   - Ajustar posición de tooltip para aparecer a un lado del puntero sin ocultar modelos.

6. **Validación de formularios**
   - Endurecer validación HTML5 + JavaScript en formularios de creación/edición de entidades.

7. **Mapa de tiendas**
   - Compactar popup/overlay hover para mejorar legibilidad y evitar recorte en bordes.

8. **Consistencia de seed/inventory**
   - Verificar y ajustar `import-data` para garantizar al menos 4 productos por estantería en todas las tiendas.

9. **Documentación final**
   - Actualizar `PRD.md`, `architecture.md`, `data_model.md` con Issue 15.
   - Crear `README.md` con instrucciones de ejecución y URL del repositorio GitHub.

## Criterios de aceptación
- Home sin bloque de estado del sistema.
- Humedad mostrada de forma coherente y estable en vistas.
- Suscripción de low stock operativa con umbral 10.
- Detalle de tienda con métricas ambientales unificadas y semáforo visual.
- Tooltip 3D enriquecido y posicionado lateralmente.
- Formularios con validaciones robustas en cliente.
- Popup del mapa compacto y completamente legible.
- Seed con mínimo 4 productos por shelf garantizado.
- Documentación técnica y funcional actualizada.
