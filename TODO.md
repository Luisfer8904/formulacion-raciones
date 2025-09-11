# TODO: Implementar Carga de Nutrientes e Ingredientes

## Pasos a completar:

### ✅ Análisis y Planificación
- [x] Analizar estructura actual del sistema
- [x] Identificar archivos relevantes
- [x] Crear plan detallado
- [x] Obtener aprobación del usuario

### 🔄 Implementación

#### 1. Modificar página de opciones
- [x] Agregar nueva sección "Gestión de Datos" en opciones.html
- [x] Incluir botones para descargar plantilla y cargar archivo
- [x] Agregar estilos CSS necesarios
- [x] Agregar funciones JavaScript para manejo de eventos

#### 2. Crear nuevas rutas en usuarios.py
- [x] Ruta `/descargar_plantilla_nutrientes_ingredientes` - Generar y descargar plantilla Excel
- [x] Ruta `/cargar_nutrientes_ingredientes` - Procesar archivo Excel cargado
- [x] Funciones de utilidad para manejo de Excel
- [x] Funciones auxiliares para conversión segura de datos

#### 3. Implementar funcionalidades
- [x] Función para generar plantilla Excel con estructura correcta
- [x] Función para procesar archivo Excel y validar datos
- [x] Función para guardar nutrientes e ingredientes en base de datos
- [x] Manejo de errores y validaciones
- [x] Soporte para actualización de datos existentes
- [x] Validación de estructura de archivo Excel

#### 4. Testing y validación
- [ ] Verificar descarga de plantilla
- [ ] Probar carga de datos desde Excel
- [ ] Validar que los datos se guarden correctamente
- [ ] Probar manejo de errores

### 📋 Estructura de la plantilla Excel:
- Hoja 1: Nutrientes (nombre, unidad, tipo)
- Hoja 2: Ingredientes (nombre, tipo, comentario, precio, ms)
- Hoja 3: Ingredientes_Nutrientes (ingrediente_nombre, nutriente_nombre, valor)

### 🔧 Dependencias necesarias:
- openpyxl (para manejo de archivos Excel)
