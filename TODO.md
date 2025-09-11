# TODO - Corrección de Hoja de Impresión

## ✅ Completado
- [x] Analizar el problema de legibilidad en la tabla de ingredientes
- [x] Identificar que los nombres se muestran en `<select>` muy pequeños
- [x] Crear plan de mejora para la hoja de impresión
- [x] Modificar `templates/operaciones/hoja_impresion.html`
  - [x] Cambiar `<select>` por texto plano más legible con `<strong>`
  - [x] Aumentar tamaño de fuente para nombres de ingredientes (14px pantalla, 13px impresión)
  - [x] Mejorar estilos CSS para impresión con clases específicas
  - [x] Optimizar ancho de columnas con porcentajes fijos
  - [x] Agregar formateo numérico con 2 decimales
  - [x] Ocultar columna de acciones en impresión con `no-print`
  - [x] Mejorar contraste y legibilidad con colores y bordes

## 🔄 En Progreso
- [ ] Actualizar en GitHub

## ⏳ Pendiente
- [ ] Probar la impresión en diferentes navegadores
- [ ] Verificar que no se afecten otras funcionalidades

## 📋 Cambios Realizados

### Mejoras en la tabla de ingredientes:
1. **Nombres más legibles**: Cambié los `<select>` pequeños por texto `<strong>` con mayor tamaño
2. **Mejor formateo**: Los valores numéricos ahora usan formato con 2 decimales
3. **Estilos optimizados**: 
   - Pantalla: 14px para nombres, fondo gris claro, borde verde
   - Impresión: 13px para nombres, padding optimizado
4. **Ancho de columnas**: Definidos con porcentajes para mejor distribución
5. **Ocultación inteligente**: Columna de acciones oculta en impresión

### Mejoras en la tabla de nutrientes:
- Aplicados los mismos principios de legibilidad
- Formateo condicional para valores opcionales
- Mejor alineación de contenido
