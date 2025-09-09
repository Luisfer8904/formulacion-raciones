#!/bin/bash

# Script para configurar Git y subir cambios
echo "🚀 Configurando Git y subiendo correcciones de herramientas..."

# Verificar si ya existe un repositorio Git
if [ ! -d ".git" ]; then
    echo "📁 Inicializando repositorio Git..."
    git init
    
    # Configurar usuario (cambiar por tus datos)
    git config user.name "FeedPro Developer"
    git config user.email "developer@feedpro.app"
else
    echo "✅ Repositorio Git ya existe"
fi

# Agregar archivos al staging
echo "📝 Agregando archivos modificados..."

# Archivos de migración y scripts
git add agregar_limites_ingredientes.sql
git add ejecutar_migracion_limites_corregido.py

# Herramientas modulares
git add app/routes/herramientas/
git add app/routes/herramientas_modular.py
git add app/routes/herramientas_api.py

# Templates y JavaScript
git add templates/operaciones/herramientas_modular.html
git add static/js/herramientas-mejoradas.js

# Archivos de configuración actualizados
git add app/__init__.py
git add app/routes/optimizacion.py

# Documentación
git add TODO_FIXES.md
git add RESUMEN_CORRECCIONES.md

# Verificar estado
echo "📊 Estado actual del repositorio:"
git status

# Hacer commit
echo "💾 Creando commit..."
git commit -m "🔧 Refactorización completa de herramientas y corrección de límites

✨ Nuevas funcionalidades:
- Herramientas modulares separadas por funcionalidad
- APIs backend robustas para cada herramienta
- Sistema de gestión de límites de ingredientes
- Migración de base de datos para límites

🚀 Mejoras de rendimiento:
- Separación de herramientas en módulos individuales
- Carga modular para evitar bloqueos
- JavaScript optimizado con manejo de errores
- APIs backend con validación

🐛 Correcciones:
- Límites de ingredientes ahora se guardan correctamente
- Requerimientos funcionando apropiadamente
- Sistema de optimización usando límites
- Herramientas funcionando con APIs backend

📁 Archivos principales:
- app/routes/herramientas/ (módulos separados)
- ejecutar_migracion_limites_corregido.py (migración BD)
- templates/operaciones/herramientas_modular.html (UI optimizada)
- static/js/herramientas-mejoradas.js (JS optimizado)

🎯 Resultado: Sistema más rápido, estable y mantenible"

echo "✅ Commit creado exitosamente!"

# Mostrar log del último commit
echo "📋 Último commit:"
git log --oneline -1

echo ""
echo "🎉 ¡Listo para subir a GitHub!"
echo "💡 Para subir a GitHub, ejecuta:"
echo "   git remote add origin <URL_DEL_REPOSITORIO>"
echo "   git branch -M main"
echo "   git push -u origin main"
