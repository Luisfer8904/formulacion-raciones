# TODO: Corrección de Herramientas y Límites

## ✅ Problemas Identificados

### 1. Herramientas (Tools) Issues:
- [x] Las herramientas son solo frontend (JavaScript) sin endpoints backend apropiados
- [x] Faltan rutas API para conversión de unidades, cálculos nutricionales, etc.
- [x] Las herramientas dependen de cálculos frontend que no funcionan correctamente

### 2. Límites y Requerimientos Issues:
- [x] El sistema de optimización espera límites de ingredientes (`limite_min`, `limite_max`) pero estos campos no existen en la tabla ingredientes
- [x] El guardado de requerimientos funciona, pero el proceso de optimización no lee los límites correctamente
- [x] Faltan columnas en la tabla ingredientes para límites

### 3. Estructura de Base de Datos Issues:
- [x] Faltan columnas para límites de ingredientes
- [x] Manejo inconsistente de datos entre frontend y backend

## 📋 Plan de Corrección

### 1. Corregir Estructura de Base de Datos:
- [x] Agregar columnas `limite_min` y `limite_max` a la tabla ingredientes
- [x] Asegurar tipos de datos y restricciones apropiadas
- [x] Crear script de migración (`ejecutar_migracion_limites_corregido.py`)

### 2. Corregir Endpoints Backend API:
- [x] Crear endpoints API apropiados para toda la funcionalidad de herramientas
- [x] Separar herramientas en módulos individuales para mejor rendimiento
- [x] Corregir el sistema de optimización para manejar límites apropiadamente
- [x] Asegurar que los requerimientos se guarden y recuperen correctamente

### 3. Corregir Integración Frontend:
- [x] Actualizar JavaScript para comunicarse apropiadamente con APIs backend
- [x] Crear template optimizado para herramientas modulares
- [x] Corregir envíos de formularios y manejo de datos
- [x] Asegurar manejo apropiado de errores y retroalimentación al usuario

### 4. Probar y Validar:
- [ ] Ejecutar migración de límites en base de datos
- [ ] Probar toda la funcionalidad de herramientas modulares
- [ ] Probar guardado/carga de requerimientos y límites
- [ ] Verificar que la optimización funcione con restricciones apropiadas

## 🎯 Orden de Implementación

1. **Estructura de Base de Datos** (Prioridad Alta)
2. **Backend API Endpoints** (Prioridad Alta)  
3. **Frontend Integration** (Prioridad Media)
4. **Testing y Validación** (Prioridad Media)

## 📝 Notas de Implementación

- Usar migraciones seguras para cambios de BD
- Mantener compatibilidad hacia atrás
- Implementar manejo robusto de errores
- Documentar cambios en API
