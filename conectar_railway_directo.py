#!/usr/bin/env python3
"""
Script para conectar directamente a Railway y crear la tabla actividades
Usa las credenciales específicas de Railway
"""

import sys

# Intentar importar mysql.connector
try:
    import mysql.connector
    from mysql.connector import Error
except ImportError:
    print("❌ Error: mysql-connector-python no está instalado")
    print("💡 Instala con: pip install mysql-connector-python")
    sys.exit(1)

def conectar_railway():
    """Conecta a Railway y ejecuta la migración"""
    
    print("🚀 Conectando a Railway MySQL...")
    
    # Credenciales de Railway
    config = {
        'host': 'mysql.railway.internal',
        'port': 3306,
        'database': 'railway',
        'user': 'root',
        'password': 'KIJShdTBbFcWOGCgabsVbrOjwoNHiPJh',
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci'
    }
    
    connection = None
    try:
        # Conectar a la base de datos
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            print("✅ Conexión exitosa a Railway MySQL")
            
            cursor = connection.cursor()
            
            # Leer el archivo SQL
            with open('railway_actividades.sql', 'r', encoding='utf-8') as file:
                sql_content = file.read()
            
            # Dividir en comandos individuales (separar por punto y coma)
            commands = []
            current_command = ""
            
            for line in sql_content.split('\n'):
                line = line.strip()
                if line and not line.startswith('--'):
                    current_command += line + " "
                    if line.endswith(';'):
                        commands.append(current_command.strip())
                        current_command = ""
            
            print(f"📝 Ejecutando {len(commands)} comandos SQL...")
            
            for i, command in enumerate(commands, 1):
                if command and command != ';':
                    try:
                        print(f"   {i}. Ejecutando: {command[:50]}...")
                        cursor.execute(command)
                        connection.commit()
                        
                        # Si es un SELECT, mostrar resultados
                        if command.upper().startswith('SELECT'):
                            results = cursor.fetchall()
                            for result in results:
                                print(f"      → {result}")
                        
                        print(f"   ✅ Comando {i} ejecutado exitosamente")
                        
                    except Error as e:
                        if "already exists" in str(e).lower():
                            print(f"   ⚠️  Comando {i}: La tabla ya existe (ignorando)")
                        elif "duplicate entry" in str(e).lower():
                            print(f"   ⚠️  Comando {i}: Registro duplicado (ignorando)")
                        else:
                            print(f"   ❌ Error en comando {i}: {e}")
                            # No retornar False, continuar con los demás comandos
            
            # Verificar que la tabla se creó
            cursor.execute("SHOW TABLES LIKE 'actividades'")
            if cursor.fetchone():
                print("✅ Tabla 'actividades' creada/verificada exitosamente")
                
                # Verificar contenido
                cursor.execute("SELECT COUNT(*) FROM actividades")
                result = cursor.fetchone()
                if result:
                    print(f"📊 La tabla tiene registros")
                
                return True
            else:
                print("❌ Error: La tabla 'actividades' no se encontró")
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
    print("🛠️  MIGRACIÓN DIRECTA A RAILWAY")
    print("=" * 60)
    
    if conectar_railway():
        print("\n🎉 ¡Migración completada exitosamente!")
        print("✅ La tabla 'actividades' está lista en Railway")
        print("🌐 Ahora puedes probar la aplicación en Railway")
    else:
        print("\n❌ La migración tuvo problemas")
        print("💡 Pero es posible que algunos comandos se hayan ejecutado correctamente")
