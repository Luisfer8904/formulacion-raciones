# TODO - Mejoras Planificador y Reportes

## ✅ COMPLETADO
- [x] Análisis de archivos existentes
- [x] Plan de implementación aprobado
- [x] **PARTE 1: Reporte Comparativo - Vista Previa PDF**
  - [x] Modificar endpoint para mostrar PDF en navegador (inline)
  - [x] Agregar endpoint separado para descarga
  - [x] Actualizar respuesta JSON con URLs de vista previa y descarga
- [x] **PARTE 2: Planificador de Producción - Base de Datos**
  - [x] Crear script SQL completo con tablas del planificador
  - [x] Implementar conexiones reales a BD en planificador.py
  - [x] Crear datos de prueba en SQL
  - [x] Actualizar APIs con datos reales (bachadas, alertas, estadísticas)

## 🔄 EN PROGRESO
- [ ] Testing de funcionalidades

## 📋 PENDIENTE
- [ ] Ejecutar script SQL en base de datos
- [ ] Probar funcionalidades en navegador
- [ ] Documentación de cambios

## 📝 CAMBIOS REALIZADOS

### Reporte Comparativo:
1. **Nuevo endpoint**: `/api/ver_reporte/<reporte_id>` - Vista previa en navegador
2. **Endpoint existente**: `/api/descargar_reporte/<reporte_id>` - Descarga forzada
3. **Headers modificados**: 
   - Vista previa: `Content-Disposition: inline`
   - Descarga: `Content-Disposition: attachment`

### Planificador de Producción:
1. **Nuevas tablas creadas** (crear_tablas_planificador.sql):
   - `bachadas` - Programación de producción
   - `inventario_ingredientes` - Control de stock
   - `movimientos_inventario` - Registro de movimientos
   - `ordenes_produccion` - Órdenes de trabajo
   - `recursos_produccion` - Personal y equipos
   - `asignacion_recursos` - Asignación de recursos
   - `actividades_produccion` - Registro de actividades
   - `alertas_inventario` - Sistema de alertas
   - `reportes_produccion` - Reportes generados

2. **APIs actualizadas** en planificador.py:
   - `obtener_bachadas()` - Conecta con tabla bachadas
   - `obtener_alertas_inventario()` - Conecta con alertas_inventario
   - `obtener_estadisticas_produccion()` - Calcula estadísticas reales

3. **Datos de ejemplo incluidos** para testing inmediato

## 🚀 PRÓXIMOS PASOS
1. Ejecutar: `mysql -u usuario -p database < crear_tablas_planificador.sql`
2. Probar vista previa de reportes en navegador
3. Verificar funcionalidades del planificador
