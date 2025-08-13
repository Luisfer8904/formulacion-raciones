#!/usr/bin/env python3
"""
Script para arreglar la tabla requerimientos en Railway
- Agregar valor por defecto a la columna 'especie'
- Verificar si existe la columna 'tipo_especie' y crearla si es necesario
"""

import mysql.connector
import os
from app.db import get_db_connection

def fix_requerimientos_table():
    """Arreglar la estructura de la tabla requerimientos"""
    try:
        print("🔄 Conectando a la base de datos...")
        conn = get_db_connection()
        if not conn:
            print("❌ Error: No se pudo conectar a la base de datos")
            return False
            
        cursor = conn.cursor()
        
        # Verificar la estructura actual de la tabla
        print("🔍 Verificando estructura actual de la tabla requerimientos...")
        cursor.execute("DESCRIBE requerimientos")
        columns = cursor.fetchall()
        
        print("📋 Estructura actual:")
        column_names = []
        for col in columns:
            column_names.append(col[0])
            print(f"   {col[0]} - {col[1]} - {col[2]} - {col[3]} - {col[4]} - {col[5]}")
        
        # Verificar si existe la columna 'especie'
        if 'especie' in column_names:
            print("✅ La columna 'especie' existe")
            
            # Agregar valor por defecto a la columna especie
            print("🔄 Agregando valor por defecto a la columna 'especie'...")
            cursor.execute("""
                ALTER TABLE requerimientos 
                MODIFY COLUMN especie VARCHAR(50) DEFAULT 'General'
            """)
            print("✅ Valor por defecto agregado a la columna 'especie'")
        else:
            print("⚠️ La columna 'especie' no existe")
        
        # Verificar si existe la columna 'tipo_especie'
        if 'tipo_especie' not in column_names:
            print("🔄 Creando columna 'tipo_especie'...")
            cursor.execute("""
                ALTER TABLE requerimientos 
                ADD COLUMN tipo_especie VARCHAR(50) DEFAULT 'General' AFTER nombre
            """)
            print("✅ Columna 'tipo_especie' creada")
        else:
            print("✅ La columna 'tipo_especie' ya existe")
        
        # Verificar si existe la columna 'comentario'
        if 'comentario' not in column_names:
            print("🔄 Creando columna 'comentario'...")
            cursor.execute("""
                ALTER TABLE requerimientos 
                ADD COLUMN comentario TEXT AFTER tipo_especie
            """)
            print("✅ Columna 'comentario' creada")
        else:
            print("✅ La columna 'comentario' ya existe")
        
        # Actualizar registros existentes que tengan valores NULL
        print("🔄 Actualizando registros con valores NULL...")
        
        # Solo actualizar tipo_especie ya que especie no existe
        cursor.execute("""
            UPDATE requerimientos 
            SET tipo_especie = 'General' 
            WHERE tipo_especie IS NULL OR tipo_especie = ''
        """)
        
        # Confirmar cambios
        conn.commit()
        
        # Mostrar estructura final
        print("\n📋 Estructura final de la tabla requerimientos:")
        cursor.execute("DESCRIBE requerimientos")
        columns = cursor.fetchall()
        for col in columns:
            print(f"   {col[0]} - {col[1]} - {col[2]} - {col[3]} - {col[4]} - {col[5]}")
        
        # Mostrar algunos registros de ejemplo
        print("\n📊 Registros actuales:")
        cursor.execute("SELECT id, nombre, tipo_especie, comentario FROM requerimientos LIMIT 5")
        registros = cursor.fetchall()
        for reg in registros:
            print(f"   ID: {reg[0]}, Nombre: {reg[1]}, Tipo: {reg[2]}, Comentario: {reg[3]}")
        
        cursor.close()
        conn.close()
        
        print("✅ Tabla requerimientos arreglada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error al arreglar la tabla: {e}")
        return False

if __name__ == "__main__":
    fix_requerimientos_table()
