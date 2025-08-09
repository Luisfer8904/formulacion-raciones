#!/usr/bin/env python3
"""
Script para limpiar archivos temporales y optimizar el rendimiento de VSCode
"""

import os
import shutil
import glob

def limpiar_archivos_temporales():
    """Elimina archivos temporales que pueden ralentizar VSCode"""
    
    print("🧹 Iniciando limpieza de archivos temporales...")
    
    # Patrones de archivos a eliminar
    patrones_eliminar = [
        "**/__pycache__",
        "**/*.pyc",
        "**/*.pyo",
        "**/.pytest_cache",
        "**/.coverage",
        "**/htmlcov",
        "**/.DS_Store",
        "**/*.log",
        "**/temp",
        "**/tmp"
    ]
    
    archivos_eliminados = 0
    carpetas_eliminadas = 0
    
    for patron in patrones_eliminar:
        for ruta in glob.glob(patron, recursive=True):
            try:
                if os.path.isfile(ruta):
                    os.remove(ruta)
                    archivos_eliminados += 1
                    print(f"  ✅ Eliminado archivo: {ruta}")
                elif os.path.isdir(ruta):
                    shutil.rmtree(ruta)
                    carpetas_eliminadas += 1
                    print(f"  ✅ Eliminada carpeta: {ruta}")
            except Exception as e:
                print(f"  ❌ Error al eliminar {ruta}: {e}")
    
    print(f"\n📊 Resumen de limpieza:")
    print(f"  - Archivos eliminados: {archivos_eliminados}")
    print(f"  - Carpetas eliminadas: {carpetas_eliminadas}")

def verificar_archivos_grandes():
    """Identifica archivos grandes que pueden afectar el rendimiento"""
    
    print("\n🔍 Verificando archivos grandes...")
    
    archivos_grandes = []
    limite_mb = 10  # 10 MB
    
    for root, dirs, files in os.walk("."):
        # Excluir ciertas carpetas
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.vscode', 'venv', 'env']]
        
        for file in files:
            ruta_completa = os.path.join(root, file)
            try:
                tamaño = os.path.getsize(ruta_completa)
                tamaño_mb = tamaño / (1024 * 1024)
                
                if tamaño_mb > limite_mb:
                    archivos_grandes.append((ruta_completa, tamaño_mb))
            except Exception as e:
                continue
    
    if archivos_grandes:
        print(f"  ⚠️ Archivos grandes encontrados (>{limite_mb}MB):")
        for archivo, tamaño in sorted(archivos_grandes, key=lambda x: x[1], reverse=True):
            print(f"    - {archivo}: {tamaño:.1f} MB")
        
        print(f"\n💡 Considera mover estos archivos a la carpeta 'otros_archivos/' o excluirlos del workspace")
    else:
        print(f"  ✅ No se encontraron archivos grandes (>{limite_mb}MB)")

def optimizar_estructura():
    """Sugiere optimizaciones para la estructura del proyecto"""
    
    print("\n🏗️ Analizando estructura del proyecto...")
    
    # Verificar si app.py es muy grande
    if os.path.exists("app.py"):
        tamaño = os.path.getsize("app.py")
        lineas = 0
        try:
            with open("app.py", 'r', encoding='utf-8') as f:
                lineas = len(f.readlines())
        except:
            pass
        
        if lineas > 500:
            print(f"  ⚠️ app.py tiene {lineas} líneas (muy grande)")
            print(f"  💡 Recomendación: Usar app_optimized.py en su lugar")
        else:
            print(f"  ✅ app.py tiene un tamaño adecuado ({lineas} líneas)")
    
    # Verificar estructura de carpetas
    carpetas_recomendadas = ['routes', 'templates', 'static']
    for carpeta in carpetas_recomendadas:
        if os.path.exists(carpeta):
            print(f"  ✅ Carpeta '{carpeta}' existe")
        else:
            print(f"  ⚠️ Carpeta '{carpeta}' no existe")

def mostrar_recomendaciones():
    """Muestra recomendaciones para mejorar el rendimiento"""
    
    print("\n🚀 RECOMENDACIONES PARA MEJORAR RENDIMIENTO:")
    print("="*60)
    
    recomendaciones = [
        "1. Usar app_optimized.py en lugar de app.py",
        "2. Instalar solo las extensiones necesarias en VSCode",
        "3. Configurar exclusiones en .vscode/settings.json",
        "4. Mover archivos grandes fuera del workspace activo",
        "5. Usar .gitignore para excluir archivos temporales",
        "6. Reiniciar VSCode después de aplicar cambios",
        "7. Considerar usar un entorno virtual (venv)",
        "8. Cerrar pestañas innecesarias en VSCode"
    ]
    
    for rec in recomendaciones:
        print(f"  {rec}")
    
    print("\n💻 COMANDOS ÚTILES:")
    print("  - Reiniciar VSCode: Cmd+Shift+P → 'Developer: Reload Window'")
    print("  - Limpiar caché: Cmd+Shift+P → 'Python: Clear Cache'")
    print("  - Ver extensiones: Cmd+Shift+X")

if __name__ == "__main__":
    print("🔧 OPTIMIZADOR DE RENDIMIENTO PARA VSCODE")
    print("="*50)
    
    limpiar_archivos_temporales()
    verificar_archivos_grandes()
    optimizar_estructura()
    mostrar_recomendaciones()
    
    print("\n✅ Optimización completada!")
    print("💡 Reinicia VSCode para aplicar todos los cambios")
