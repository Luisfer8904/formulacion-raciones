import mysql.connector

# Configuración de conexión
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": "3306",
    "database": "db_nutriapp",
    "user": "root",
    "password": "root1234"
}

def crear_tabla_usuarios():
    """Crear la tabla de usuarios si no existe"""
    
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS usuarios (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL,
        correo VARCHAR(100) NOT NULL UNIQUE,
        contrasena VARCHAR(100) NOT NULL,
        rol VARCHAR(20) NOT NULL DEFAULT 'admin',
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    try:
        cursor.execute(create_table_sql)
        print("✅ Tabla 'usuarios' creada exitosamente")
        
    except Exception as e:
        print(f"❌ Error al crear la tabla: {e}")
    
    finally:
        cursor.close()
        conn.close()

def crear_usuario_admin():
    """Crear usuario administrador"""
    
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Datos del usuario admin
    admin_data = {
        'nombre': 'Administrador',
        'correo': 'admin@test.com',
        'contrasena': 'admin123',
        'rol': 'admin'
    }
    
    try:
        # Verificar si el usuario ya existe
        cursor.execute("SELECT id FROM usuarios WHERE correo = %s", (admin_data['correo'],))
        if cursor.fetchone() is not None:
            print("ℹ️ El usuario administrador ya existe")
            return
        
        # Insertar nuevo usuario
        cursor.execute("""
            INSERT INTO usuarios (nombre, correo, contrasena, rol)
            VALUES (%s, %s, %s, %s)
        """, (
            admin_data['nombre'],
            admin_data['correo'],
            admin_data['contrasena'],
            admin_data['rol']
        ))
        
        conn.commit()
        print("✅ Usuario administrador creado exitosamente")
        print(f"   Correo: {admin_data['correo']}")
        print(f"   Contraseña: {admin_data['contrasena']}")
        
    except Exception as e:
        print(f"❌ Error al crear usuario: {e}")
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("🔄 Creando tabla de usuarios...")
    crear_tabla_usuarios()
    
    print("\n🔄 Creando usuario administrador...")
    crear_usuario_admin()
