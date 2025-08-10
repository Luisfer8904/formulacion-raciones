#!/usr/bin/env python3
"""
Script para agregar la columna tipo_especie a la tabla requerimientos
"""

import mysql.connector
import os
from app.db import DB_CONFIG

def agregar_columna_tipo_especie():
    """Agrega la columna tipo_especie a la tabla requerimientos si no existe"""
    try:
        # Conectar a la base de datos
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("🔄 Verificando estructura de la tabla requerimientos...")
        
        # Verificar si la columna ya existe
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s 
            AND TABLE_NAME = 'requerimientos' 
            AND COLUMN_NAME = 'tipo_especie'
        """, (DB_CONFIG['database'],))
        
        resultado = cursor.fetchone()
        
        if resultado:
            print("✅ La columna 'tipo_especie' ya existe en la tabla requerimientos")
        else:
            print("➕ Agregando columna 'tipo_especie' a la tabla requerimientos...")
            
            # Agregar la columna
            cursor.execute("""
                ALTER TABLE requerimientos 
                ADD COLUMN tipo_especie VARCHAR(50) DEFAULT 'General' AFTER nombre
            """)
            
            conn.commit()
            print("✅ Columna 'tipo_especie' agregada exitosamente")
            
            # Actualizar registros existentes con un valor por defecto
            cursor.execute("""
                UPDATE requerimientos 
                SET tipo_especie = 'General' 
                WHERE tipo_especie IS NULL
            """)
            
            conn.commit()
            print("✅ Registros existentes actualizados con valor por defecto")
        
        # Mostrar estructura actual de la tabla
        cursor.execute("DESCRIBE requerimientos")
        columnas = cursor.fetchall()
        
        print("\n📋 Estructura actual de la tabla requerimientos:")
        for columna in columnas:
            nombre_columna = columna[0]
            tipo_columna = columna[1]
            print(f"   - {nombre_columna} ({tipo_columna})")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Proceso completado exitosamente")
        
    except mysql.connector.Error as e:
        print(f"❌ Error de base de datos: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando proceso de actualización de base de datos...")
    agregar_columna_tipo_especie()
