#!/usr/bin/env python3
"""
Script para ejecutar la migración de la tabla de actividades
"""

import mysql.connector
from mysql.connector import Error
import os
from typing import Any

# Intentar cargar dotenv si está disponible
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv no está instalado, usando variables de entorno del sistema")

def ejecutar_migracion():
    """Ejecuta la migración para crear la tabla de actividades"""
    
    # Configuración de la base de datos
    config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'formulacion_nutricional'),
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci'
    }
    
    try:
        # Conectar a la base de datos
        print("🔗 Conectando a la base de datos...")
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        # Leer el archivo SQL
        print("📖 Leyendo archivo de migración...")
        with open('crear_tabla_actividades.sql', 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        # Dividir las consultas por punto y coma
        queries = [query.strip() for query in sql_content.split(';') if query.strip()]
        
        print("🚀 Ejecutando migración...")
        for query in queries:
            if query:
                cursor.execute(query)
                print(f"✅ Ejecutado: {query[:50]}...")
        
        # Confirmar cambios
        connection.commit()
        print("✅ Migración completada exitosamente!")
        
        # Verificar que la tabla se creó correctamente
        cursor.execute("SHOW TABLES LIKE 'actividades'")
        result = cursor.fetchone()
        
        if result:
            print("✅ Tabla 'actividades' creada correctamente")
            
            # Mostrar estructura de la tabla
            cursor.execute("DESCRIBE actividades")
            columns = cursor.fetchall()
            print("\n📋 Estructura de la tabla 'actividades':")
            for column in columns:
                column_typed: Any = column
                print(f"  - {column_typed[0]}: {column_typed[1]}")
                
            # Contar registros de ejemplo
            cursor.execute("SELECT COUNT(*) FROM actividades")
            count_result: Any = cursor.fetchone()
            count = count_result[0] if count_result else 0
            print(f"\n📊 Registros de ejemplo insertados: {count}")
            
        else:
            print("❌ Error: La tabla 'actividades' no se encontró")
            
    except Error as e:
        print(f"❌ Error durante la migración: {e}")
        
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("🔌 Conexión cerrada")

if __name__ == "__main__":
    print("🎯 Iniciando migración de la tabla de actividades...")
    ejecutar_migracion()
