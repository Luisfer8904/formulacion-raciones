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
        username VARCHAR(50) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        email VARCHAR(100),
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    try:
        cursor.execute(create_table_sql)
        print("✅ Tabla 'usuarios' creada exitosamente")
        
        # Crear usuario admin por defecto
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE username = 'admin'")
        result = cursor.fetchone()
        if result and result[0] == 0:
            cursor.execute(
                "INSERT INTO usuarios (username, password, email) VALUES (%s, %s, %s)",
                ('admin', 'admin123', 'admin@formulacion.com')
            )
            print("✅ Usuario admin creado")
        
        conn.commit()
        
    except Exception as e:
        print(f"❌ Error al crear tabla usuarios: {e}")
    
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
        unidad VARCHAR(20),
        descripcion TEXT,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    try:
        cursor.execute(create_table_sql)
        print("✅ Tabla 'nutrientes' creada exitosamente")
        
        # Insertar nutrientes básicos
        nutrientes_basicos = [
            ('Proteína Bruta', '%', 'Contenido de proteína bruta'),
            ('Energía Metabolizable', 'Kcal/kg', 'Energía metabolizable'),
            ('Fibra Bruta', '%', 'Contenido de fibra bruta'),
            ('Grasa Bruta', '%', 'Contenido de grasa bruta'),
            ('Cenizas', '%', 'Contenido de cenizas'),
            ('Calcio', '%', 'Contenido de calcio'),
            ('Fósforo', '%', 'Contenido de fósforo'),
            ('Lisina', '%', 'Aminoácido lisina'),
            ('Metionina', '%', 'Aminoácido metionina'),
            ('Humedad', '%', 'Contenido de humedad')
        ]
        
        for nombre, unidad, descripcion in nutrientes_basicos:
            cursor.execute("SELECT COUNT(*) FROM nutrientes WHERE nombre = %s", (nombre,))
            result = cursor.fetchone()
            if result and result[0] == 0:
                cursor.execute(
                    "INSERT INTO nutrientes (nombre, unidad, descripcion) VALUES (%s, %s, %s)",
                    (nombre, unidad, descripcion)
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
        precio DECIMAL(10,2),
        comentarios TEXT,
        materia_seca DECIMAL(8,4),
        proteina_bruta DECIMAL(8,4),
        energia_metabolizable DECIMAL(8,4),
        fibra_bruta DECIMAL(8,4),
        grasa_bruta DECIMAL(8,4),
        cenizas DECIMAL(8,4),
        calcio DECIMAL(8,4),
        fosforo DECIMAL(8,4),
        lisina DECIMAL(8,4),
        metionina DECIMAL(8,4),
        humedad DECIMAL(8,4),
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    try:
        cursor.execute(create_table_sql)
        print("✅ Tabla 'ingredientes' creada exitosamente")
        
        # Insertar algunos ingredientes básicos
        ingredientes_basicos = [
            ('Maíz amarillo', 350.00, 'Cereal energético', 88.0, 8.5, 3350, 2.2, 3.8, 1.3, 0.03, 0.28, 0.25, 0.18, 12.0),
            ('Soya integral', 450.00, 'Fuente de proteína', 90.0, 37.0, 3200, 6.0, 18.0, 5.5, 0.24, 0.65, 2.4, 0.54, 10.0),
            ('Torta de soya', 420.00, 'Subproducto proteico', 89.0, 44.0, 2230, 7.0, 1.5, 6.8, 0.29, 0.71, 2.8, 0.62, 11.0),
            ('Salvado de trigo', 280.00, 'Subproducto fibroso', 88.0, 15.5, 1900, 11.0, 4.0, 5.8, 0.13, 1.18, 0.65, 0.22, 12.0),
            ('Carbonato de calcio', 150.00, 'Fuente de calcio', 100.0, 0.0, 0, 0.0, 0.0, 100.0, 38.0, 0.0, 0.0, 0.0, 0.0)
        ]
        
        for ingrediente in ingredientes_basicos:
            cursor.execute("SELECT COUNT(*) FROM ingredientes WHERE nombre = %s", (ingrediente[0],))
            result = cursor.fetchone()
            if result and result[0] == 0:
                cursor.execute("""
                    INSERT INTO ingredientes 
                    (nombre, precio, comentarios, materia_seca, proteina_bruta, energia_metabolizable, 
                     fibra_bruta, grasa_bruta, cenizas, calcio, fosforo, lisina, metionina, humedad) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, ingrediente)
        
        print("✅ Ingredientes básicos insertados")
        conn.commit()
        
    except Exception as e:
        print(f"❌ Error al crear tabla ingredientes: {e}")
    
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
        especie VARCHAR(50) NOT NULL,
        categoria VARCHAR(100) NOT NULL,
        peso_inicial DECIMAL(8,2),
        peso_final DECIMAL(8,2),
        proteina_bruta DECIMAL(8,4),
        energia_metabolizable DECIMAL(8,4),
        fibra_bruta_max DECIMAL(8,4),
        grasa_bruta_max DECIMAL(8,4),
        calcio DECIMAL(8,4),
        fosforo DECIMAL(8,4),
        lisina DECIMAL(8,4),
        metionina DECIMAL(8,4),
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    try:
        cursor.execute(create_table_sql)
        print("✅ Tabla 'requerimientos' creada exitosamente")
        
        # Insertar requerimientos básicos
        requerimientos_basicos = [
            ('Pollo', 'Iniciación (0-21 días)', 0.04, 0.9, 23.0, 3000, 4.0, 8.0, 1.0, 0.45, 1.44, 0.50),
            ('Pollo', 'Crecimiento (22-35 días)', 0.9, 2.0, 20.0, 3100, 5.0, 8.0, 0.9, 0.42, 1.29, 0.46),
            ('Pollo', 'Finalización (36-42 días)', 2.0, 2.5, 18.0, 3150, 6.0, 8.0, 0.8, 0.38, 1.16, 0.42),
            ('Cerdo', 'Lechones (5-10 kg)', 5.0, 10.0, 22.0, 3400, 3.0, 6.0, 0.8, 0.65, 1.35, 0.46),
            ('Cerdo', 'Crecimiento (10-30 kg)', 10.0, 30.0, 18.0, 3300, 4.0, 6.0, 0.7, 0.60, 1.15, 0.38),
            ('Cerdo', 'Engorde (30-100 kg)', 30.0, 100.0, 16.0, 3250, 6.0, 6.0, 0.6, 0.50, 0.95, 0.30)
        ]
        
        for req in requerimientos_basicos:
            cursor.execute("SELECT COUNT(*) FROM requerimientos WHERE especie = %s AND categoria = %s", (req[0], req[1]))
            result = cursor.fetchone()
            if result and result[0] == 0:
                cursor.execute("""
                    INSERT INTO requerimientos 
                    (especie, categoria, peso_inicial, peso_final, proteina_bruta, energia_metabolizable, 
                     fibra_bruta_max, grasa_bruta_max, calcio, fosforo, lisina, metionina) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, req)
        
        print("✅ Requerimientos básicos insertados")
        conn.commit()
        
    except Exception as e:
        print(f"❌ Error al crear tabla requerimientos: {e}")
    
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
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        usuario_id INT,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
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

def crear_tabla_mezcla_ingredientes():
    """Crear tabla de ingredientes por mezcla"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS mezcla_ingredientes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        mezcla_id INT NOT NULL,
        ingrediente_id INT NOT NULL,
        porcentaje DECIMAL(8,4) NOT NULL,
        cantidad_kg DECIMAL(10,4),
        costo DECIMAL(10,2),
        FOREIGN KEY (mezcla_id) REFERENCES mezclas(id) ON DELETE CASCADE,
        FOREIGN KEY (ingrediente_id) REFERENCES ingredientes(id)
    )
    """
    
    try:
        cursor.execute(create_table_sql)
        print("✅ Tabla 'mezcla_ingredientes' creada exitosamente")
        conn.commit()
        
    except Exception as e:
        print(f"❌ Error al crear tabla mezcla_ingredientes: {e}")
    
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
        
        # Crear todas las tablas
        crear_tabla_usuarios()
        crear_tabla_nutrientes()
        crear_tabla_ingredientes()
        crear_tabla_requerimientos()
        crear_tabla_mezclas()
        crear_tabla_mezcla_ingredientes()
        
        print("\n🎉 ¡Base de datos inicializada exitosamente!")
        print("\n📋 Credenciales por defecto:")
        print("   Usuario: admin")
        print("   Contraseña: admin123")
        
    except Exception as e:
        print(f"❌ Error al conectar con la base de datos: {e}")
        print("🔍 Verifica que las variables de entorno estén configuradas correctamente")

if __name__ == "__main__":
    main()
