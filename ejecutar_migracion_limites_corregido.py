#!/usr/bin/env python3
"""
Script para ejecutar la migración de límites de ingredientes
Agrega las columnas limite_min y limite_max a la tabla ingredientes
"""

import mysql.connector
import os
from typing import Any, Dict, List, Optional
from app.db import get_db_connection

def ejecutar_migracion_limites():
    """Ejecuta la migración para agregar columnas de límites a ingredientes"""
    try:
        print("🔄 Iniciando migración de límites de ingredientes...")
        
        # Obtener conexión a la base de datos
        conn = get_db_connection()
        if not conn:
            print("❌ Error: No se pudo conectar a la base de datos")
            return False
            
        cursor = conn.cursor(dictionary=True)
        print("✅ Conexión a la base de datos exitosa")
        
        # Verificar si las columnas ya existen
        print("🔍 Verificando estructura actual de la tabla ingredientes...")
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'ingredientes'
            AND COLUMN_NAME IN ('limite_min', 'limite_max')
        """)
        
        columnas_existentes: List[Dict[str, Any]] = cursor.fetchall()
        columnas_nombres = [str(col.get('COLUMN_NAME', '')) for col in columnas_existentes]
        
        print(f"📋 Columnas de límites existentes: {columnas_nombres}")
        
        # Agregar limite_min si no existe
        if 'limite_min' not in columnas_nombres:
            print("➕ Agregando columna limite_min...")
            cursor.execute("""
                ALTER TABLE ingredientes 
                ADD COLUMN limite_min DECIMAL(5,2) DEFAULT 0.00 
                COMMENT 'Límite mínimo de inclusión (%)'
            """)
            print("✅ Columna limite_min agregada exitosamente")
        else:
            print("ℹ️ La columna limite_min ya existe")
            
        # Agregar limite_max si no existe
        if 'limite_max' not in columnas_nombres:
            print("➕ Agregando columna limite_max...")
            cursor.execute("""
                ALTER TABLE ingredientes 
                ADD COLUMN limite_max DECIMAL(5,2) DEFAULT 100.00 
                COMMENT 'Límite máximo de inclusión (%)'
            """)
            print("✅ Columna limite_max agregada exitosamente")
        else:
            print("ℹ️ La columna limite_max ya existe")
        
        # Confirmar cambios
        conn.commit()
        
        # Mostrar estructura actualizada
        print("\n📋 Estructura actualizada de la tabla ingredientes:")
        cursor.execute("DESCRIBE ingredientes")
        columnas: List[Dict[str, Any]] = cursor.fetchall()
        
        for columna in columnas:
            tipo = str(columna.get('Type', ''))
            nulo = 'NULL' if columna.get('Null') == 'YES' else 'NOT NULL'
            default = f"DEFAULT {columna.get('Default', '')}" if columna.get('Default') else ''
            field = str(columna.get('Field', ''))
            print(f"   {field}: {tipo} {nulo} {default}")
        
        # Verificar datos existentes
        cursor.execute("SELECT COUNT(*) as total FROM ingredientes")
        resultado: Optional[Dict[str, Any]] = cursor.fetchone()
        total_ingredientes = int(resultado.get('total', 0)) if resultado else 0
        print(f"\n📊 Total de ingredientes en la tabla: {total_ingredientes}")
        
        if total_ingredientes > 0:
            print("🔄 Actualizando valores por defecto para ingredientes existentes...")
            cursor.execute("""
                UPDATE ingredientes 
                SET limite_min = 0.00, limite_max = 100.00 
                WHERE limite_min IS NULL OR limite_max IS NULL
            """)
            conn.commit()
            print("✅ Valores por defecto actualizados")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Migración completada exitosamente!")
        print("📝 Las columnas limite_min y limite_max han sido agregadas a la tabla ingredientes")
        print("💡 Los ingredientes existentes tienen valores por defecto: min=0.00%, max=100.00%")
        
        return True
        
    except mysql.connector.Error as e:
        print(f"❌ Error de MySQL: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def verificar_migracion():
    """Verifica que la migración se haya ejecutado correctamente"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que las columnas existen
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'ingredientes'
            AND COLUMN_NAME IN ('limite_min', 'limite_max')
            ORDER BY COLUMN_NAME
        """)
        
        columnas: List[Dict[str, Any]] = cursor.fetchall()
        
        if len(columnas) == 2:
            print("✅ Verificación exitosa: Ambas columnas de límites existen")
            for col in columnas:
                column_name = str(col.get('COLUMN_NAME', ''))
                data_type = str(col.get('DATA_TYPE', ''))
                default_value = str(col.get('COLUMN_DEFAULT', ''))
                print(f"   {column_name}: {data_type} (default: {default_value})")
            return True
        else:
            print(f"❌ Verificación fallida: Solo se encontraron {len(columnas)} columnas de 2 esperadas")
            return False
            
    except Exception as e:
        print(f"❌ Error en verificación: {e}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🚀 Ejecutando migración de límites de ingredientes...")
    print("=" * 60)
    
    if ejecutar_migracion_limites():
        print("\n" + "=" * 60)
        print("🔍 Verificando migración...")
        if verificar_migracion():
            print("\n🎉 ¡Migración completada y verificada exitosamente!")
        else:
            print("\n⚠️ Migración completada pero la verificación falló")
    else:
        print("\n❌ La migración falló")
