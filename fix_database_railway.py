#!/usr/bin/env python3
"""
Script para agregar la columna tipo_especie a la tabla requerimientos en Railway
"""

import mysql.connector
import os

def get_railway_db_config():
    """Obtiene la configuración de la base de datos desde las variables de entorno de Railway"""
    return {
        "host": os.environ.get('MYSQLHOST', '127.0.0.1'),
        "port": int(os.environ.get('MYSQLPORT', '3306')),
        "database": os.environ.get('MYSQLDATABASE', 'formulacion_nutricional'),
        "user": os.environ.get('MYSQLUSER', 'root'),
        "password": os.environ.get('MYSQLPASSWORD', 'root1234')
    }

def agregar_columna_tipo_especie():
    """Agrega la columna tipo_especie a la tabla requerimientos si no existe"""
    try:
        # Obtener configuración de Railway o local
        db_config = get_railway_db_config()
        
        print("🔄 Conectando a la base de datos...")
        print(f"   Host: {db_config['host']}")
        print(f"   Database: {db_config['database']}")
        print(f"   User: {db_config['user']}")
        
        # Conectar a la base de datos
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        print("✅ Conexión exitosa")
        print("🔄 Verificando estructura de la tabla requerimientos...")
        
        # Verificar si la columna ya existe
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s 
            AND TABLE_NAME = 'requerimientos' 
            AND COLUMN_NAME = 'tipo_especie'
        """, (db_config['database'],))
        
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
                WHERE tipo_especie IS NULL OR tipo_especie = ''
            """)
            
            conn.commit()
            print("✅ Registros existentes actualizados con valor por defecto")
        
        # Mostrar estructura actual de la tabla
        cursor.execute("DESCRIBE requerimientos")
        columnas = cursor.fetchall()
        
        print("\n📋 Estructura actual de la tabla requerimientos:")
        for columna in columnas:
            nombre_columna = str(columna[0])
            tipo_columna = str(columna[1])
            print(f"   - {nombre_columna} ({tipo_columna})")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Proceso completado exitosamente")
        return True
        
    except mysql.connector.Error as e:
        print(f"❌ Error de base de datos: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando proceso de actualización de base de datos en Railway...")
    success = agregar_columna_tipo_especie()
    if success:
        print("✅ Base de datos actualizada correctamente")
    else:
        print("❌ Error al actualizar la base de datos")
        exit(1)
