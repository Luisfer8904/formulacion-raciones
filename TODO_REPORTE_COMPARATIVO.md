# TODO: Arreglar Reporte Comparativo de Fórmulas

## Problemas Identificados:
- [x] No carga la composición nutricional (problemas de nombres de campos)
- [x] Debería seleccionar nutrientes para comparación (existe pero tiene bugs)
- [x] Debería mostrar interfaz similar a calculadora nutricional (modal)
- [x] Debería mostrarse en ventana emergente como la imagen

## Plan de Implementación:

### 1. Arreglar Backend (app/routes/reporte_comparativo.py)
- [x] Corregir inconsistencias en nombres de campos
- [x] Asegurar que `obtener_formulas_usuario` retorne `num_ingredientes`
- [x] Mejorar manejo de errores

### 2. Crear Interfaz Modal
- [x] Agregar modal en herramientas.html
- [x] Crear JavaScript para el modal
- [x] Implementar diseño similar a calculadora de aportes

### 3. Arreglar JavaScript
- [x] Corregir referencias a campos incorrectos
- [x] Mejorar carga de composición nutricional
- [x] Arreglar selección de nutrientes
- [x] Agregar validaciones y notificaciones

### 4. Mejorar UX
- [x] Agregar indicadores de carga
- [x] Mejorar interfaz de selección de nutrientes
- [x] Agregar mensajes de error claros
- [x] Asegurar diseño responsivo

## Archivos a Modificar:
- app/routes/reporte_comparativo.py
- templates/operaciones/herramientas.html
- static/js/ (nuevo archivo para modal)

## Estado: COMPLETADO ✅

## Cambios Realizados:

### Backend (app/routes/reporte_comparativo.py):
- ✅ Agregado campo `num_ingredientes` para compatibilidad con frontend
- ✅ Mantenido `total_ingredientes` para compatibilidad con otros componentes

### Frontend:
- ✅ Creado `static/js/reporte-comparativo-modal.js` con funcionalidad completa del modal
- ✅ Modificado `templates/operaciones/herramientas.html` para usar el modal
- ✅ Agregados estilos CSS para el modal
- ✅ Implementada interfaz similar a la calculadora de aportes nutricionales

### Funcionalidades Implementadas:
- ✅ Modal emergente como se solicitó
- ✅ Selección de dos fórmulas para comparar
- ✅ Carga de composición nutricional de cada fórmula
- ✅ Selección múltiple de nutrientes para comparar
- ✅ Botones "Seleccionar Todos" y "Deseleccionar Todos"
- ✅ Comparación detallada con diferencias absolutas y porcentuales
- ✅ Resumen estadístico de la comparación
- ✅ Indicadores de carga y notificaciones de estado
- ✅ Validaciones y manejo de errores
- ✅ Diseño responsivo

## Próximos Pasos:
- [ ] Probar la funcionalidad en el navegador
- [ ] Verificar que todas las APIs funcionen correctamente
- [ ] Ajustar estilos si es necesario
