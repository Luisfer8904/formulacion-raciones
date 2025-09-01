# INSTRUCCIONES PARA CREAR TABLAS EN BASE DE DATOS

## 🚀 APLICACIÓN FUNCIONANDO
La aplicación está corriendo en: **http://localhost:5001**

## 🔑 USUARIOS DE PRUEBA (Hardcodeados)
```
admin@formulacion.com / admin123 (Plan Profesional)
profesional@test.com / test123 (Plan Profesional)  
personal@test.com / test123 (Plan Personal)
basico@test.com / test123 (Plan Básico)
```

## 📋 TABLAS REQUERIDAS PARA FUNCIONALIDAD COMPLETA

### 1. TABLA PRINCIPAL: `tipo_plan` en usuarios
**EJECUTAR PRIMERO:**
```sql
-- Agregar columna tipo_plan a tabla usuarios existente
ALTER TABLE usuarios ADD COLUMN tipo_plan ENUM('basico', 'personal', 'profesional') DEFAULT 'basico';

-- Actualizar usuario admin existente
UPDATE usuarios SET tipo_plan = 'profesional' WHERE email = 'admin@formulacion.com';
```

### 2. TABLAS DEL PLANIFICADOR (Opcional - para funcionalidad avanzada)
**Archivo completo:** `crear_tablas_planificador.sql`

**Tablas principales:**
- `bachadas` - Programación de producción
- `inventario_ingredientes` - Control de stock  
- `movimientos_inventario` - Registro entradas/salidas
- `ordenes_produccion` - Órdenes de trabajo
- `recursos_produccion` - Personal y equipos
- `asignacion_recursos` - Asignación a bachadas
- `actividades_produccion` - Registro detallado
- `alertas_inventario` - Sistema de alertas
- `reportes_produccion` - Reportes generados

## ✅ FUNCIONALIDADES DISPONIBLES AHORA

### CON TABLA `tipo_plan` SOLAMENTE:
- ✅ Login funcional con usuarios de prueba
- ✅ Panel con pestañas "Reportes" y "Planificador" visibles
- ✅ Reportes comparativos con vista previa (sin descarga forzada)
- ✅ Interfaz del planificador con datos simulados

### CON TODAS LAS TABLAS:
- ✅ Todo lo anterior +
- ✅ Planificador conectado a base de datos real
- ✅ Gestión completa de inventarios
- ✅ Sistema de alertas automáticas
- ✅ Reportes de producción avanzados

## 🎯 RECOMENDACIÓN

**PASO 1 (MÍNIMO):** Ejecutar solo la modificación de `usuarios`:
```sql
ALTER TABLE usuarios ADD COLUMN tipo_plan ENUM('basico', 'personal', 'profesional') DEFAULT 'basico';
UPDATE usuarios SET tipo_plan = 'profesional' WHERE email = 'admin@formulacion.com';
```

**PASO 2 (COMPLETO):** Si quieres funcionalidad avanzada, ejecutar todo el archivo `crear_tablas_planificador.sql`

## 🔧 CÓMO PROBAR

1. **Ejecutar la modificación mínima de usuarios**
2. **Ir a:** http://localhost:5001/login
3. **Login con:** admin@formulacion.com / admin123
4. **Verificar:** Que aparezcan las pestañas "Reportes" y "Planificador"
5. **Probar:** Generar reporte comparativo (debería mostrar vista previa)

## 📁 ARCHIVOS IMPORTANTES

- `crear_tablas_planificador.sql` - Script completo de tablas
- `agregar_tipo_plan_usuarios.sql` - Solo modificación usuarios
- `app/routes/reportes_mejorado.py` - Reportes con vista previa
- `app/routes/auth.py` - Sistema de login con usuarios hardcodeados

## 🎉 RESULTADO ESPERADO

Después de ejecutar la modificación mínima:
- Login funcionará correctamente
- Panel mostrará todas las opciones profesionales
- Reportes mostrarán vista previa en navegador
- Planificador mostrará interfaz completa con datos simulados
