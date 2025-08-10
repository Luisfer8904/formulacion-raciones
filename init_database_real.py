import mysql.connector
import os
from typing import Optional

# Configuración de conexión usando variables de entorno
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "127.0.0.1"),
    "port": os.environ.get("DB_PORT", "3306"),
    "database": os.environ.get("DB_DATABASE", "formulacion_nutricional"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", "root1234")
}

def get_db_connection():
    """Obtiene una conexión a la base de datos"""
    return mysql.connector.connect(**DB_CONFIG)

def crear_tabla_usuarios():
    """Crear tabla de usuarios"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS usuarios (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        rol ENUM('admin', 'user') DEFAULT 'user',
        pais VARCHAR(50),
        moneda VARCHAR(10),
        tipo_moneda VARCHAR(20),
        unidad_medida VARCHAR(20),
        idioma VARCHAR(10) DEFAULT 'es',
        tema VARCHAR(20) DEFAULT 'claro',
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    try:
        cursor.execute(create_table_sql)
        print("✅ Tabla 'usuarios' creada exitosamente")
        
        # Crear usuario admin por defecto
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE email = 'admin@formulacion.com'")
        result = cursor.fetchone()
        if result and result[0] == 0:
            cursor.execute("""
                INSERT INTO usuarios (nombre, email, password, rol) 
                VALUES (%s, %s, %s, %s)
            """, ('Administrador', 'admin@formulacion.com', 'admin123', 'admin'))
            print("✅ Usuario admin creado (email: admin@formulacion.com, password: admin123)")
        
        conn.commit()
        
    except Exception as e:
        print(f"❌ Error al crear tabla usuarios: {e}")
    
    finally:
        cursor.close()
        conn.close()

def crear_tabla_especies():
    """Crear tabla de especies"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS especies (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(50) NOT NULL,
        descripcion TEXT,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    try:
        cursor.execute(create_table_sql)
        print("✅ Tabla 'especies' creada exitosamente")
        
        # Insertar especies básicas
        especies_basicas = [
            ('Pollo', 'Pollos de engorde'),
            ('Cerdo', 'Cerdos de engorde'),
            ('Bovino', 'Ganado bovino'),
            ('Ovino', 'Ganado ovino'),
            ('Caprino', 'Ganado caprino'),
            ('Peces', 'Acuicultura'),
            ('Conejos', 'Cunicultura')
        ]
        
        for nombre, descripcion in especies_basicas:
            cursor.execute("SELECT COUNT(*) FROM especies WHERE nombre = %s", (nombre,))
            result = cursor.fetchone()
            if result and result[0] == 0:
                cursor.execute(
                    "INSERT INTO especies (nombre, descripcion) VALUES (%s, %s)",
                    (nombre, descripcion)
                )
        
        print("✅ Especies básicas insertadas")
        conn.commit()
        
    except Exception as e:
        print(f"❌ Error al crear tabla especies: {e}")
    
    finally:
        cursor.close()
        conn.close()

def crear_tabla_nutrientes():
    """Crear tabla de nutrientes"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS nutrientes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL,
        unidad VARCHAR(20) NOT NULL,
        tipo VARCHAR(50),
        usuario_id INT,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
    )
    """
    
    try:
        cursor.execute(create_table_sql)
        print("✅ Tabla 'nutrientes' creada exitosamente")
        
        # Obtener ID del usuario admin
        cursor.execute("SELECT id FROM usuarios WHERE email = 'admin@formulacion.com'")
        admin_result = cursor.fetchone()
        admin_id = admin_result[0] if admin_result else 1
        
        # Insertar nutrientes básicos
        nutrientes_basicos = [
            ('Proteína Bruta', '%', 'Macronutriente'),
            ('Energía Metabolizable', 'Kcal/kg', 'Energía'),
            ('Fibra Bruta', '%', 'Macronutriente'),
            ('Grasa Bruta', '%', 'Macronutriente'),
            ('Cenizas', '%', 'Macronutriente'),
            ('Materia Seca', '%', 'Composición'),
            ('Calcio', '%', 'Mineral'),
            ('Fósforo', '%', 'Mineral'),
            ('Sodio', '%', 'Mineral'),
            ('Potasio', '%', 'Mineral'),
            ('Magnesio', '%', 'Mineral'),
            ('Lisina', '%', 'Aminoácido'),
            ('Metionina', '%', 'Aminoácido'),
            ('Treonina', '%', 'Aminoácido'),
            ('Triptófano', '%', 'Aminoácido'),
            ('Arginina', '%', 'Aminoácido')
        ]
        
        for nombre, unidad, tipo in nutrientes_basicos:
            cursor.execute("SELECT COUNT(*) FROM nutrientes WHERE nombre = %s AND usuario_id = %s", (nombre, admin_id))
            result = cursor.fetchone()
            if result and result[0] == 0:
                cursor.execute(
                    "INSERT INTO nutrientes (nombre, unidad, tipo, usuario_id) VALUES (%s, %s, %s, %s)",
                    (nombre, unidad, tipo, admin_id)
                )
        
        print("✅ Nutrientes básicos insertados")
        conn.commit()
        
    except Exception as e:
        print(f"❌ Error al crear tabla nutrientes: {e}")
    
    finally:
        cursor.close()
        conn.close()

def crear_tabla_ingredientes():
    """Crear tabla de ingredientes"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS ingredientes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(255) NOT NULL,
        comentario TEXT,
        tipo VARCHAR(100),
        precio DECIMAL(10,2),
        ms DECIMAL(8,4),
        usuario_id INT NOT NULL,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
    )
    """
    
    try:
        cursor.execute(create_table_sql)
        print("✅ Tabla 'ingredientes' creada exitosamente")
        conn.commit()
        
    except Exception as e:
        print(f"❌ Error al crear tabla ingredientes: {e}")
    
    finally:
        cursor.close()
        conn.close()

def crear_tabla_ingredientes_nutrientes():
    """Crear tabla de relación ingredientes-nutrientes"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS ingredientes_nutrientes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        ingrediente_id INT NOT NULL,
        nutriente_id INT NOT NULL,
        valor DECIMAL(10,4),
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (ingrediente_id) REFERENCES ingredientes(id) ON DELETE CASCADE,
        FOREIGN KEY (nutriente_id) REFERENCES nutrientes(id) ON DELETE CASCADE,
        UNIQUE KEY unique_ingrediente_nutriente (ingrediente_id, nutriente_id)
    )
    """
    
    try:
        cursor.execute(create_table_sql)
        print("✅ Tabla 'ingredientes_nutrientes' creada exitosamente")
        conn.commit()
        
    except Exception as e:
        print(f"❌ Error al crear tabla ingredientes_nutrientes: {e}")
    
    finally:
        cursor.close()
        conn.close()

def crear_tabla_ingrediente_especie():
    """Crear tabla de relación ingrediente-especie"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS ingrediente_especie (
        id INT AUTO_INCREMENT PRIMARY KEY,
        ingrediente_id INT NOT NULL,
        especie_id INT NOT NULL,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (ingrediente_id) REFERENCES ingredientes(id) ON DELETE CASCADE,
        FOREIGN KEY (especie_id) REFERENCES especies(id) ON DELETE CASCADE,
        UNIQUE KEY unique_ingrediente_especie (ingrediente_id, especie_id)
    )
    """
    
    try:
        cursor.execute(create_table_sql)
        print("✅ Tabla 'ingrediente_especie' creada exitosamente")
        conn.commit()
        
    except Exception as e:
        print(f"❌ Error al crear tabla ingrediente_especie: {e}")
    
    finally:
        cursor.close()
        conn.close()

def crear_tabla_mezclas():
    """Crear tabla de mezclas/formulaciones"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS mezclas (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(255) NOT NULL,
        descripcion TEXT,
        especie VARCHAR(50),
        categoria VARCHAR(100),
        costo_total DECIMAL(10,2),
        usuario_id INT NOT NULL,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
    )
    """
    
    try:
        cursor.execute(create_table_sql)
        print("✅ Tabla 'mezclas' creada exitosamente")
        conn.commit()
        
    except Exception as e:
        print(f"❌ Error al crear tabla mezclas: {e}")
    
    finally:
        cursor.close()
        conn.close()

def crear_tabla_requerimientos():
    """Crear tabla de requerimientos nutricionales"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS requerimientos (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(255) NOT NULL,
        especie VARCHAR(50) NOT NULL,
        categoria VARCHAR(100) NOT NULL,
        descripcion TEXT,
        usuario_id INT NOT NULL,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
    )
    """
    
    try:
        cursor.execute(create_table_sql)
        print("✅ Tabla 'requerimientos' creada exitosamente")
        conn.commit()
        
    except Exception as e:
        print(f"❌ Error al crear tabla requerimientos: {e}")
    
    finally:
        cursor.close()
        conn.close()

def main():
    """Función principal para inicializar todas las tablas"""
    print("🚀 Iniciando creación de base de datos...")
    print(f"📍 Conectando a: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    
    try:
        # Verificar conexión
        conn = get_db_connection()
        conn.close()
        print("✅ Conexión a base de datos exitosa")
        
        # Crear todas las tablas en orden correcto (respetando foreign keys)
        crear_tabla_usuarios()
        crear_tabla_especies()
        crear_tabla_nutrientes()
        crear_tabla_ingredientes()
        crear_tabla_ingredientes_nutrientes()
        crear_tabla_ingrediente_especie()
        crear_tabla_mezclas()
        crear_tabla_requerimientos()
        
        print("\n🎉 ¡Base de datos inicializada exitosamente!")
        print("\n📋 Credenciales por defecto:")
        print("   Email: admin@formulacion.com")
        print("   Contraseña: admin123")
        print("   Rol: admin")
        
    except Exception as e:
        print(f"❌ Error al conectar con la base de datos: {e}")
        print("🔍 Verifica que las variables de entorno estén configuradas correctamente")

if __name__ == "__main__":
    main()
