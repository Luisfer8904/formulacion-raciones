import mysql.connector
import os
from typing import Optional

# Configuración para Railway (usando variables de entorno)
RAILWAY_CONFIG = {
    "host": os.environ.get("MYSQLHOST", "localhost"),
    "port": int(os.environ.get("MYSQLPORT", "3306")),
    "database": os.environ.get("MYSQLDATABASE", "railway"),
    "user": os.environ.get("MYSQLUSER", "root"),
    "password": os.environ.get("MYSQLPASSWORD", "")
}

def get_railway_connection():
    """Obtiene una conexión a la base de datos de Railway"""
    try:
        conn = mysql.connector.connect(**RAILWAY_CONFIG)
        print("✅ Conexión exitosa a Railway MySQL")
        return conn
    except Exception as e:
        print(f"❌ Error conectando a Railway: {e}")
        return None

def actualizar_requerimientos():
    """Actualizar tabla de requerimientos con datos completos"""
    conn = get_railway_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    try:
        # Primero verificar si existen usuarios
        cursor.execute("SELECT id FROM usuarios WHERE email = 'admin@formulacion.com' LIMIT 1")
        admin_result = cursor.fetchone()
        admin_id = admin_result[0] if admin_result else 1
        
        # Verificar usuario_id 3 (que aparece en los datos)
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE id = 3")
        user3_exists = cursor.fetchone()[0] > 0
        
        if not user3_exists:
            # Crear usuario con id 3 si no existe
            cursor.execute("""
                INSERT IGNORE INTO usuarios (id, nombre, email, password, rol, fecha_creacion) 
                VALUES (3, 'Usuario Formulador', 'formulador@test.com', 'pass123', 'user', NOW())
            """)
            print("✅ Usuario con ID 3 creado")
        
        # Limpiar requerimientos existentes para evitar duplicados
        cursor.execute("DELETE FROM conjuntos_requerimientos")
        cursor.execute("DELETE FROM requerimientos WHERE id NOT IN (4, 6)")
        
        # Insertar requerimientos adicionales que faltan
        requerimientos_adicionales = [
            (7, 'Cerdo Iniciador', 'Cerdo', 'Iniciador', 'Requerimientos para cerdos en etapa de iniciación', 3),
            (8, 'Cerdo Crecimiento', 'Cerdo', 'Crecimiento', 'Requerimientos para cerdos en crecimiento', 3),
            (9, 'Cerdo Finalización', 'Cerdo', 'Finalización', 'Requerimientos para cerdos en finalización', 3),
            (10, 'Pollo Iniciador', 'Aves', 'Iniciador', 'Requerimientos para pollos en etapa de iniciación', 3),
            (11, 'Pollo Crecimiento', 'Aves', 'Crecimiento', 'Requerimientos para pollos en crecimiento', 3),
            (12, 'Pollo Finalización', 'Aves', 'Finalización', 'Requerimientos para pollos en finalización', 3),
            (13, 'Gallina Ponedora', 'Aves', 'Postura', 'Requerimientos para gallinas ponedoras', 3),
            (14, 'Bovino Lechero', 'Bovino', 'Producción', 'Requerimientos para vacas lecheras', 3),
            (15, 'Bovino Engorde', 'Bovino', 'Engorde', 'Requerimientos para bovinos de engorde', 3)
        ]
        
        for req_data in requerimientos_adicionales:
            cursor.execute("""
                INSERT IGNORE INTO requerimientos (id, nombre, especie, categoria, descripcion, usuario_id, fecha_creacion)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """, req_data)
        
        # Actualizar conjuntos_requerimientos con más datos
        conjuntos_adicionales = [
            # Bovino Adulto (id=4)
            (4, 11, 0.4),  # Calcio mínimo
            (4, 12, 0.25), # Fósforo mínimo
            (4, 15, 0.15), # Azufre
            (4, 28, 8.0),  # Proteína Equivalente
            (4, 30, 2200), # Energía Digestible
            
            # Bovino Crecimiento (id=6)
            (6, 11, 0.6),  # Calcio
            (6, 12, 0.35), # Fósforo
            (6, 15, 0.2),  # Azufre
            (6, 28, 12.0), # Proteína Equivalente
            (6, 30, 2800), # Energía Digestible
            
            # Cerdo Iniciador (id=7)
            (7, 1, 20.0),  # Proteína Bruta
            (7, 2, 0.8),   # Calcio
            (7, 3, 0.65),  # Fósforo
            
            # Pollo Iniciador (id=10)
            (10, 18, 23.0), # Proteína Bruta
            (10, 19, 3000), # Energía Metabolizable
            
            # Gallina Ponedora (id=13)
            (13, 18, 16.0), # Proteína Bruta
            (13, 19, 2750), # Energía Metabolizable
        ]
        
        for req_id, nutriente_id, valor in conjuntos_adicionales:
            cursor.execute("""
                INSERT IGNORE INTO conjuntos_requerimientos (requerimiento_id, nutriente_id, valor_sugerido)
                VALUES (%s, %s, %s)
            """, (req_id, nutriente_id, valor))
        
        conn.commit()
        print("✅ Requerimientos actualizados exitosamente")
        
        # Mostrar resumen
        cursor.execute("SELECT COUNT(*) FROM requerimientos")
        total_req = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM conjuntos_requerimientos")
        total_conj = cursor.fetchone()[0]
        
        print(f"📊 Total requerimientos: {total_req}")
        print(f"📊 Total conjuntos de requerimientos: {total_conj}")
        
    except Exception as e:
        print(f"❌ Error actualizando requerimientos: {e}")
        conn.rollback()
    
    finally:
        cursor.close()
        conn.close()

def verificar_estructura():
    """Verificar la estructura actual de la base de datos"""
    conn = get_railway_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    try:
        # Verificar tablas existentes
        cursor.execute("SHOW TABLES")
        tablas = [tabla[0] for tabla in cursor.fetchall()]
        print(f"📋 Tablas existentes: {', '.join(tablas)}")
        
        # Verificar requerimientos
        cursor.execute("SELECT id, nombre, especie, categoria FROM requerimientos ORDER BY id")
        requerimientos = cursor.fetchall()
        print("\n📋 Requerimientos actuales:")
        for req in requerimientos:
            print(f"   ID {req[0]}: {req[1]} ({req[2]} - {req[3]})")
        
        # Verificar nutrientes
        cursor.execute("SELECT COUNT(*) FROM nutrientes")
        total_nutrientes = cursor.fetchone()[0]
        print(f"\n📊 Total nutrientes: {total_nutrientes}")
        
        # Verificar ingredientes
        cursor.execute("SELECT COUNT(*) FROM ingredientes")
        total_ingredientes = cursor.fetchone()[0]
        print(f"📊 Total ingredientes: {total_ingredientes}")
        
    except Exception as e:
        print(f"❌ Error verificando estructura: {e}")
    
    finally:
        cursor.close()
        conn.close()

def main():
    """Función principal"""
    print("🚀 Actualizando base de datos de Railway...")
    print("🔍 Verificando estructura actual...")
    
    verificar_estructura()
    
    print("\n🔄 Actualizando requerimientos...")
    actualizar_requerimientos()
    
    print("\n✅ Actualización completada!")
    print("\n🔍 Verificando estructura final...")
    verificar_estructura()

if __name__ == "__main__":
    main()
