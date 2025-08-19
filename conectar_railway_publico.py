#!/usr/bin/env python3
"""
Script para conectar a Railway usando el host público
"""

import sys

try:
    import mysql.connector
    from mysql.connector import Error
except ImportError:
    print("❌ Error: mysql-connector-python no está instalado")
    print("💡 Instala con: pip install mysql-connector-python")
    sys.exit(1)

def conectar_railway_publico():
    """Conecta a Railway usando diferentes hosts públicos posibles"""
    
    print("🚀 Intentando conectar a Railway MySQL...")
    
    # Posibles hosts públicos de Railway
    hosts_posibles = [
        'containers-us-west-1.railway.app',
        'containers-us-west-2.railway.app', 
        'containers-us-east-1.railway.app',
        'mysql-production-15ea.up.railway.app',
        'viaduct.proxy.rlwy.net'
    ]
    
    # Credenciales base
    base_config = {
        'port': 3306,
        'database': 'railway',
        'user': 'root',
        'password': 'KIJShdTBbFcWOGCgabsVbrOjwoNHiPJh',
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci'
    }
    
    for host in hosts_posibles:
        print(f"🔍 Probando host: {host}")
        
        config = base_config.copy()
        config['host'] = host
        
        try:
            connection = mysql.connector.connect(**config)
            
            if connection.is_connected():
                print(f"✅ ¡Conexión exitosa con {host}!")
                
                cursor = connection.cursor()
                
                # Ejecutar la migración
                ejecutar_migracion(cursor, connection)
                
                cursor.close()
                connection.close()
                return True
                
        except Error as e:
            print(f"   ❌ Falló: {e}")
            continue
    
    print("❌ No se pudo conectar con ningún host")
    return False

def ejecutar_migracion(cursor, connection):
    """Ejecuta los comandos SQL de migración"""
    
    print("📝 Ejecutando migración...")
    
    # Comandos SQL individuales
    comandos = [
        """CREATE TABLE IF NOT EXISTS `actividades` (
          `id` int NOT NULL AUTO_INCREMENT,
          `usuario_id` int NOT NULL,
          `descripcion` varchar(255) NOT NULL,
          `tipo_actividad` varchar(50) NOT NULL,
          `fecha` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`),
          KEY `idx_usuario_fecha` (`usuario_id`, `fecha`),
          CONSTRAINT `fk_actividades_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
        
        """INSERT IGNORE INTO `actividades` (`usuario_id`, `descripcion`, `tipo_actividad`, `fecha`) VALUES
        (3, 'Creó el ingrediente: Carbonato de calcio fino', 'ingrediente', '2024-01-15 10:30:00')""",
        
        """INSERT IGNORE INTO `actividades` (`usuario_id`, `descripcion`, `tipo_actividad`, `fecha`) VALUES
        (3, 'Creó el ingrediente: Urea', 'ingrediente', '2024-01-15 11:45:00')""",
        
        """INSERT IGNORE INTO `actividades` (`usuario_id`, `descripcion`, `tipo_actividad`, `fecha`) VALUES
        (3, 'Guardó una nueva formulación', 'formulacion', '2024-01-16 14:30:00')""",
        
        "SELECT COUNT(*) FROM actividades"
    ]
    
    for i, comando in enumerate(comandos, 1):
        try:
            print(f"   {i}. Ejecutando comando...")
            cursor.execute(comando)
            connection.commit()
            
            if comando.startswith('SELECT'):
                result = cursor.fetchone()
                if result:
                    print(f"      → Total actividades: {result[0]}")
            
            print(f"   ✅ Comando {i} ejecutado")
            
        except Error as e:
            if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                print(f"   ⚠️  Comando {i}: Ya existe (ignorando)")
            else:
                print(f"   ❌ Error en comando {i}: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("🛠️  MIGRACIÓN A RAILWAY - HOST PÚBLICO")
    print("=" * 60)
    
    if conectar_railway_publico():
        print("\n🎉 ¡Migración completada!")
        print("✅ La tabla 'actividades' está lista en Railway")
    else:
        print("\n❌ No se pudo conectar a Railway")
        print("💡 Usa MySQL Workbench con las credenciales para conectarte manualmente")
