# TODO - Corrección de Pestañas por Tipo de Usuario

## Problema Identificado
- Las pestañas no se muestran según el tipo de usuario
- Todos los usuarios ven todas las pestañas (herramientas + reportes + planificador)
- El problema está en el valor por defecto del `tipo_plan` en auth.py

## Plan de Corrección

### ✅ Completado
- [x] Análisis del problema
- [x] Identificación de la causa raíz
- [x] Revisión de archivos clave (layout.html, auth.py, usuarios.py, etc.)

### 🔄 En Progreso
- [x] Corregir valor por defecto de tipo_plan en auth.py
- [x] Verificar usuarios de prueba
- [ ] Probar funcionalidad

### ⏳ Pendiente
- [ ] Verificar que no hay otros errores en la aplicación
- [ ] Documentar la solución

## Detalles Técnicos

### Causa del Problema
En `app/routes/auth.py` línea 67:
```python
session['tipo_plan'] = 'profesional'  # Por defecto para testing
```

### Solución
Cambiar el valor por defecto a 'basico' para que los usuarios sin tipo_plan definido solo vean herramientas.

### Usuarios de Prueba Configurados
- admin@formulacion.com: profesional (admin)
- profesional@test.com: profesional 
- personal@test.com: personal
- basico@test.com: basico

### Lógica de Pestañas (layout.html)
- Herramientas: todos los usuarios
- Reportes: personal, profesional y admin
- Planificador: profesional y admin
