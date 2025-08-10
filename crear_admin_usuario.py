import mysql.connector

# Configuración de conexión actualizada
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": "3306",
    "database": "formulacion_nutricional",
    "user": "root",
    "password": "root1234"
}

def crear_usuario_admin():
    """Crear usuario administrador"""
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Datos del usuario admin
        admin_data = {
            'nombre': 'Administrador FeedPro',
            'email': 'admin@feedpro.com',
            'password': 'admin123',
            'rol': 'admin',
            'pais': 'Honduras',
            'moneda': 'HNL',
            'tipo_moneda': 'Nacional',
            'unidad_medida': 'kg',
            'idioma': 'es',
            'tema': 'claro'
        }
        
        # Verificar si el usuario ya existe
        cursor.execute("SELECT id FROM usuarios WHERE email = %s", (admin_data['email'],))
        if cursor.fetchone() is not None:
            print("ℹ️ El usuario administrador ya existe")
            
            # Actualizar la contraseña por si acaso
            cursor.execute("""
                UPDATE usuarios 
                SET password = %s, nombre = %s 
                WHERE email = %s
            """, (admin_data['password'], admin_data['nombre'], admin_data['email']))
            conn.commit()
            print("✅ Contraseña del administrador actualizada")
        else:
            # Insertar nuevo usuario
            cursor.execute("""
                INSERT INTO usuarios (nombre, email, password, rol, pais, moneda, tipo_moneda, unidad_medida, idioma, tema)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                admin_data['nombre'],
                admin_data['email'],
                admin_data['password'],
                admin_data['rol'],
                admin_data['pais'],
                admin_data['moneda'],
                admin_data['tipo_moneda'],
                admin_data['unidad_medida'],
                admin_data['idioma'],
                admin_data['tema']
            ))
            conn.commit()
            print("✅ Usuario administrador creado exitosamente")
        
        print(f"   Email: {admin_data['email']}")
        print(f"   Contraseña: {admin_data['password']}")
        
    except Exception as e:
        print(f"❌ Error al crear/actualizar usuario: {e}")
    
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🔄 Creando/actualizando usuario administrador...")
    crear_usuario_admin()
