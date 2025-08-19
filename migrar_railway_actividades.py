#!/usr/bin/env python3
"""
Script para ejecutar la migración de la tabla actividades en Railway
Usa las variables de entorno de Railway para conectarse a la base de datos
"""

import os
import sys

# Intentar importar mysql.connector
try:
    import mysql.connector
    from mysql.connector import Error
except ImportError:
    print("❌ Error: mysql-connector-python no está instalado")
    print("💡 Instala con: pip install mysql-connector-python")
    sys.exit(1)

def obtener_credenciales_railway():
    """Obtiene las credenciales de Railway desde las variables de entorno"""
    
    # Variables típicas de Railway para MySQL
    host = os.getenv('MYSQLHOST') or os.getenv('DB_HOST')
    port = os.getenv('MYSQLPORT') or os.getenv('DB_PORT', '3306')
    database = os.getenv('MYSQLDATABASE') or os.getenv('DB_NAME')
    user = os.getenv('MYSQLUSER') or os.getenv('DB_USER')
    password = os.getenv('MYSQLPASSWORD') or os.getenv('DB_PASSWORD')
    
    # También intentar con DATABASE_URL si está disponible
    database_url = os.getenv('DATABASE_URL')
    if database_url and not all([host, user, password, database]):
        print("🔍 Intentando extraer credenciales de DATABASE_URL...")
        # Parsear DATABASE_URL si es necesario
        # mysql://user:password@host:port/database
        if database_url.startswith('mysql://'):
            import urllib.parse
            parsed = urllib.parse.urlparse(database_url)
            host = parsed.hostname
            port = parsed.port or 3306
            user = parsed.username
            password = parsed.password
            database = parsed.path.lstrip('/')
    
    return {
        'host': host,
        'port': int(port) if port else 3306,
        'database': database,
        'user': user,
        'password': password
    }

def ejecutar_migracion_railway():
    """Ejecuta la migración en Railway"""
    
    print("🚀 Iniciando migración de actividades en Railway...")
    
    # Obtener credenciales
    credenciales = obtener_credenciales_railway()
    
    # Verificar que tenemos todas las credenciales
    if not all(credenciales.values()):
        print("❌ Error: No se pudieron obtener todas las credenciales de Railway")
        print("📋 Variables de entorno disponibles:")
        for key in ['MYSQLHOST', 'MYSQLPORT', 'MYSQLDATABASE', 'MYSQLUSER', 'MYSQLPASSWORD', 'DATABASE_URL']:
            value = os.getenv(key)
            if value:
                if 'PASSWORD' in key:
                    print(f"   {key}: {'*' * len(value)}")
                else:
                    print(f"   {key}: {value}")
            else:
                print(f"   {key}: (no definida)")
        return False
    
    print(f"🔗 Conectando a Railway MySQL: {credenciales['host']}:{credenciales['port']}")
    
    connection = None
    try:
        # Conectar a la base de datos
        connection = mysql.connector.connect(
            host=credenciales['host'],
            port=credenciales['port'],
            database=credenciales['database'],
            user=credenciales['user'],
            password=credenciales['password'],
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        
        if connection.is_connected():
            print("✅ Conexión exitosa a Railway MySQL")
            
            cursor = connection.cursor()
            
            # Leer el archivo SQL
            with open('crear_tabla_actividades.sql', 'r', encoding='utf-8') as file:
                sql_content = file.read()
            
            # Dividir en comandos individuales
            commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip()]
            
            print(f"📝 Ejecutando {len(commands)} comandos SQL...")
            
            for i, command in enumerate(commands, 1):
                if command:
                    try:
                        print(f"   {i}. Ejecutando comando...")
                        cursor.execute(command)
                        connection.commit()
                        print(f"   ✅ Comando {i} ejecutado exitosamente")
                    except Error as e:
                        if "already exists" in str(e).lower():
                            print(f"   ⚠️  Comando {i}: La tabla ya existe (ignorando)")
                        else:
                            print(f"   ❌ Error en comando {i}: {e}")
                            return False
            
            # Verificar que la tabla se creó
            cursor.execute("SHOW TABLES LIKE 'actividades'")
            if cursor.fetchone():
                print("✅ Tabla 'actividades' creada/verificada exitosamente")
                
                # Verificar registros en la tabla
                try:
                    cursor.execute("SELECT COUNT(*) FROM actividades")
                    print("📊 Tabla 'actividades' verificada y accesible")
                except Error:
                    print("⚠️  No se pudo verificar el contenido de la tabla")
                
                return True
            else:
                print("❌ Error: La tabla 'actividades' no se encontró después de la migración")
                return False
                
    except Error as e:
        print(f"❌ Error de conexión a Railway: {e}")
        return False
        
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("🔌 Conexión cerrada")

if __name__ == "__main__":
    print("=" * 60)
    print("🛠️  MIGRACIÓN DE TABLA ACTIVIDADES - RAILWAY")
    print("=" * 60)
    
    if ejecutar_migracion_railway():
        print("\n🎉 ¡Migración completada exitosamente!")
        print("✅ La tabla 'actividades' está lista para usar en Railway")
    else:
        print("\n❌ La migración falló")
        print("💡 Verifica las variables de entorno de Railway")
        sys.exit(1)
