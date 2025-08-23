# Sistema de Formulación de Raciones 🐄🐷🐔

Sistema web profesional para la formulación nutricional de alimentos balanceados para animales, desarrollado con Flask y optimizado para producción.

## 🚀 Características Principales

### 📊 Gestión de Ingredientes
- Base de datos completa de ingredientes con valores nutricionales
- Importación masiva desde archivos CSV/Excel
- Edición y actualización de composición nutricional
- Control de precios y disponibilidad

### 🧪 Formulación Inteligente
- **Optimización Matemática**: Algoritmos avanzados usando SciPy
- **Múltiples Especies**: Bovinos, porcinos, aves, etc.
- **Formulación por Minerales**: Especializada para suplementos
- **Restricciones Flexibles**: Límites mínimos y máximos personalizables

### 📈 Sistema de Planes
- **Planes Dinámicos**: Básico, Personal, Profesional, Premium, Enterprise
- **Mejora de Plan**: Sistema de solicitudes con notificaciones automáticas
- **Cancelación Inteligente**: Proceso guiado con retroalimentación

### 📧 Notificaciones Automáticas
- Integración con SendGrid API
- Fallback SMTP para máxima confiabilidad
- Notificaciones de cambios de plan
- Sistema de actividades y logging

## 🛠️ Tecnologías

- **Backend**: Flask 2.3.3 + Python 3.8+
- **Base de Datos**: MySQL 8.0
- **Optimización**: NumPy + SciPy
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Email**: SendGrid API / SMTP
- **Deployment**: Railway, Docker, Gunicorn

## 📦 Instalación

### Requisitos Previos
```bash
Python 3.8+
MySQL 8.0+
Git
```

### Configuración Local
```bash
# Clonar repositorio
git clone https://github.com/Luisfer8904/formulacion-raciones.git
cd formulacion-raciones

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones
```

### Variables de Entorno
```env
# Base de Datos
DB_HOST=localhost
DB_PORT=3306
DB_USER=tu_usuario
DB_PASSWORD=tu_password
DB_NAME=formulacion_raciones

# Email (SendGrid)
SENDER_EMAIL=tu_email@dominio.com
SENDER_PASSWORD=tu_sendgrid_api_key
RECIPIENT_EMAIL=admin@dominio.com

# Flask
SECRET_KEY=tu_clave_secreta_muy_segura
FLASK_DEBUG=False
```

### Inicializar Base de Datos
```bash
# Ejecutar script de inicialización
python init_database.py

# Crear usuario administrador
python crear_admin_usuario.py
```

## 🚀 Ejecución

### Desarrollo
```bash
python run.py
```
La aplicación estará disponible en `http://localhost:5001`

### Producción
```bash
gunicorn -c gunicorn.conf.py run:app
```

## 📁 Estructura del Proyecto

```
formulacion-raciones/
├── app/                          # Aplicación principal
│   ├── __init__.py              # Factory de la app
│   ├── db.py                    # Conexión a base de datos
│   └── routes/                  # Rutas organizadas por módulos
│       ├── auth.py              # Autenticación
│       ├── ingredientes.py      # Gestión de ingredientes
│       ├── nutrientes.py        # Gestión de nutrientes
│       ├── requerimientos.py    # Requerimientos nutricionales
│       ├── mezclas.py           # Gestión de mezclas
│       ├── optimizacion.py      # Motor de optimización
│       └── usuarios.py          # Gestión de usuarios y planes
├── templates/                   # Plantillas HTML
│   ├── sitio/                   # Páginas públicas
│   └── operaciones/             # Panel de administración
├── static/                      # Archivos estáticos
│   ├── css/                     # Estilos
│   ├── js/                      # JavaScript
│   └── img_productos/           # Imágenes
├── otros_archivos/              # Utilidades y scripts
├── run.py                       # Punto de entrada
├── requirements.txt             # Dependencias
├── Dockerfile                   # Configuración Docker
├── Procfile                     # Configuración Railway
└── gunicorn.conf.py            # Configuración Gunicorn
```

## 🔧 Funcionalidades Avanzadas

### Motor de Optimización
- **Algoritmo**: Programación lineal con restricciones
- **Objetivos**: Minimización de costos
- **Restricciones**: Nutricionales, de ingredientes, personalizadas
- **Múltiples Soluciones**: Genera alternativas optimizadas

### Sistema de Usuarios
- **Autenticación**: Sesiones seguras
- **Roles**: Administrador, Usuario
- **Actividades**: Logging completo de acciones
- **Planes**: Sistema dinámico de suscripciones

### API Endpoints
```
GET  /api/ingrediente/<id>       # Datos de ingrediente
POST /optimizar_formulacion      # Optimización de fórmulas
GET  /api/lista_mezclas         # Lista de mezclas guardadas
```

## 🐳 Docker

```bash
# Construir imagen
docker build -t formulacion-raciones .

# Ejecutar contenedor
docker run -p 5001:5001 --env-file .env formulacion-raciones
```

## 🚀 Deployment en Railway

1. Conectar repositorio de GitHub
2. Configurar variables de entorno
3. Railway detectará automáticamente la configuración
4. La aplicación se desplegará usando `Procfile`

## 📊 Base de Datos

### Tablas Principales
- `ingredientes`: Catálogo de ingredientes
- `nutrientes`: Valores nutricionales
- `requerimientos`: Necesidades por especie
- `mezclas`: Fórmulas guardadas
- `usuarios`: Gestión de usuarios
- `actividades`: Log de actividades

## 🤝 Contribuir

1. Fork del proyecto
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 👨‍💻 Autor

**Luis Rivera** - [Luisfer8904](https://github.com/Luisfer8904)

## 🆘 Soporte

Para soporte técnico o consultas:
- 📧 Email: [Configurar en variables de entorno]
- 🐛 Issues: [GitHub Issues](https://github.com/Luisfer8904/formulacion-raciones/issues)

---

⭐ **¡Dale una estrella si este proyecto te fue útil!**
