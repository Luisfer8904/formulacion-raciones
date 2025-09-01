# TODO - Calculadora de Aportes Nutricionales

## Progreso de Implementación

### Backend
- [x] Agregar API `/api/calcular_aportes_nutricionales` en herramientas.py
- [x] Agregar API `/api/obtener_ingredientes` para cargar ingredientes
- [x] Agregar API `/api/obtener_nutrientes` para cargar nutrientes
- [x] Agregar API `/api/obtener_valores_nutricionales` para obtener valores específicos

### Frontend
- [x] Agregar nueva tarjeta de herramienta en herramientas.html
- [x] Crear modal con formulario para entrada de datos
- [x] Implementar JavaScript para cálculos y visualización
- [x] Crear tabla de resultados
- [x] Actualizar estadísticas de herramientas (6 activas)

### Impresión
- [x] Crear template de impresión `imprimir_aportes.html`
- [x] Implementar ruta de impresión en backend
- [x] Conectar funcionalidad de impresión con JavaScript

### Testing
- [ ] Probar funcionalidad básica
- [ ] Verificar cálculos
- [ ] Probar impresión

## Funcionalidades Implementadas
- [x] Backend APIs completas (obtener ingredientes, nutrientes, calcular aportes)
- [x] Frontend con modal interactivo
- [x] Interfaz de usuario completa
- [x] Sistema de cálculos nutricionales
- [x] Visualización de resultados en tablas
- [x] Sistema de impresión
- [x] Validaciones de entrada
- [x] Manejo de errores
- [x] **NUEVA**: Cargar fórmulas existentes desde el sistema
- [x] **NUEVA**: APIs para obtener mezclas y detalles de mezclas
- [x] **MEJORADA**: Lista desplegable para selección de fórmulas (reemplaza modal)
- [x] **MEJORADA**: Filtrado de ingredientes y nutrientes por usuario
- [x] **MEJORADA**: Carga automática de ingredientes al seleccionar fórmula

## Próximos Pasos
1. ✅ Implementar backend APIs
2. ✅ Agregar interfaz frontend  
3. ✅ Crear sistema de impresión
4. ✅ **NUEVO**: Implementar carga de fórmulas existentes
5. ✅ **NUEVO**: Refactorizar y separar herramientas en módulos
6. 🔄 Testing completo (pendiente)

## Resumen
La "Calculadora de Aportes Nutricionales" ha sido implementada exitosamente como una nueva herramienta en el sistema. Permite a los usuarios:
- Crear fórmulas personalizadas con ingredientes y porcentajes
- **NUEVO**: Cargar fórmulas ya creadas desde el sistema principal
- Seleccionar nutrientes específicos para analizar
- Calcular aportes nutricionales y consumo diario por animal
- Visualizar resultados detallados en tablas
- Imprimir reportes profesionales
- No guarda registros (solo cálculos temporales)

## Funcionalidad de Carga de Fórmulas
- Botón "Cargar Fórmula" junto al campo de nombre
- Modal con lista de fórmulas existentes del usuario
- Información detallada: nombre, tipo de animales, etapa, fecha
- Carga automática de ingredientes y porcentajes
- Interfaz intuitiva con selección visual
- Manejo de errores y estados de carga
