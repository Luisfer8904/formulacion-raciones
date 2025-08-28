# TODO - Mejoras de Nutrientes y Estilos

## ✅ Completado

### 1. Tipos de Nutrientes
- [x] Agregados tipos "Aditivos" y "Otros" en formularios
- [x] Actualizada validación en backend para incluir nuevos tipos
- [x] Modificados templates de nuevo_nutriente.html y editar_nutriente.html
- [x] Organizados tipos alfabéticamente en formularios

### 2. Ordenamiento Alfabético
- [x] Modificada consulta SQL en ver_nutrientes() para ordenar por nombre ASC
- [x] Los nutrientes ahora se muestran ordenados alfabéticamente

### 3. Estilos Consistentes de Títulos
- [x] Unificado header en herramientas.html con estilo feedpro-header
- [x] Unificado header en planificador.html con estilo feedpro-header  
- [x] Unificado header en reportes.html con estilo feedpro-header
- [x] Todos los títulos ahora usan el mismo estilo consistente

### 4. Favicon en Login
- [x] Agregadas referencias de favicon en templates/sitio/login.html
- [x] Incluidos favicon.ico y Favicon.png para compatibilidad

### 5. Archivos Modificados
- [x] app/routes/nutrientes.py - Nuevos tipos y ordenamiento
- [x] templates/operaciones/nuevo_nutriente.html - Tipos actualizados
- [x] templates/operaciones/editar_nutriente.html - Tipos actualizados
- [x] templates/sitio/login.html - Favicon agregado
- [x] templates/operaciones/herramientas.html - Header unificado
- [x] templates/operaciones/planificador.html - Header unificado
- [x] templates/operaciones/reportes.html - Header unificado

## 🔄 Pendiente

### 6. Actualización en GitHub
- [ ] Commit de todos los cambios
- [ ] Push al repositorio remoto

## 📝 Notas Técnicas

### Tipos de Nutrientes Disponibles (Alfabético):
1. Aditivo
2. Energético  
3. Mineral
4. Otros
5. Proteico

### Cambios en Base de Datos:
- No se requieren cambios en esquema de BD
- Los nuevos tipos se validan a nivel de aplicación
- Ordenamiento se maneja con ORDER BY en consultas

### Estilos Unificados:
- Todos los headers usan clase `feedpro-header`
- Estructura consistente: `<h2>` con icono + `<small>` para descripción
- Animación `fade-in-up` aplicada uniformemente
