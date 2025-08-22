# Plan de Mejoras del Sitio Web FeedPro

## Progreso de Implementación

### ✅ Completado
- [x] 1. **Consistencia de Email**
  - [x] Actualizar footer de "info@feedpro.com" a "feedpro07@gmail.com"
  - [x] Verificar otras referencias de email en el sitio

- [x] 2. **Corrección de Branding en Login**
  - [x] Cambiar título de "Iniciar Sesión | Nutrición Animal" a "Iniciar Sesión | FeedPro"

- [x] 3. **Funcionalidad del Formulario de Demo**
  - [x] Agregar action al formulario para usar ruta `/procesar_solicitud`
  - [x] Implementar JavaScript para manejo del formulario
  - [x] Conectar con la funcionalidad de email existente
  - [x] Actualizar ruta en usuarios.py para manejar tipo "demo"

- [x] 4. **Testimonial Real**
  - [x] Reemplazar "Juan Pérez - Granja Avícola El Progreso" 
  - [x] Implementar "Cosme Rivera - Concentrados San Francisco"
  - [x] Agregar logo de la empresa (san_francisco.png)
  - [x] Actualizar texto del testimonial

- [x] 5. **Consistencia de CTAs**
  - [x] Unificar botones a "Empezar prueba gratis (14 días)" en página de precios
  - [x] Mantener "Contactar ventas" solo para plan Institucional

- [x] 6. **Limpieza del Hero**
  - [x] Cambiar texto "Tecnología" por "Innovación"

- [x] 7. **Ocultar Recursos**
  - [x] Ocultar menú "Recursos" temporalmente
  - [x] Comentar enlaces a /libros en navegación

### 🔄 En Progreso
- Ninguna tarea en progreso

### ⏳ Pendiente
- Ninguna tarea pendiente

## Archivos a Modificar
- `templates/sitio/index.html` (demo form, testimonial, hero)
- `templates/sitio/login.html` (título)
- `templates/sitio/precios.html` (CTAs)
- `templates/sitio/pie.html` (email)
- `templates/sitio/cabecera.html` (ocultar recursos)

## Notas
- Email de contacto: feedpro07@gmail.com
- Logo de San Francisco ya existe en static/san_francisco.png
- Testimonial: Cosme Rivera agradece mejor control de fórmulas
