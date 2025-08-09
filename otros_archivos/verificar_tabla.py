import mysql.connector

# Configuración de conexión
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": "3306",
    "database": "db_nutriapp",
    "user": "root",
    "password": "root1234"
}

def verificar_tabla():
    """Verificar que la tabla se creó correctamente y mostrar algunos datos"""
    
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Contar registros
        cursor.execute("SELECT COUNT(*) as total FROM ingredientes_completos")
        total = cursor.fetchone()
        print(f"📊 Total de ingredientes en la tabla: {total['total']}")
        
        # Mostrar algunos ejemplos
        cursor.execute("SELECT INGREDIENTES, PRECIO, PB, Ca, P, LYS, MET FROM ingredientes_completos LIMIT 5")
        ejemplos = cursor.fetchall()
        
        print("\n📋 Ejemplos de datos importados:")
        print("-" * 80)
        for ingrediente in ejemplos:
            print(f"Ingrediente: {ingrediente['INGREDIENTES']}")
            print(f"  Precio: {ingrediente['PRECIO']}")
            print(f"  Proteína: {ingrediente['PB']}%")
            print(f"  Calcio: {ingrediente['Ca']}%")
            print(f"  Fósforo: {ingrediente['P']}%")
            print(f"  Lisina: {ingrediente['LYS']}%")
            print(f"  Metionina: {ingrediente['MET']}%")
            print("-" * 40)
        
        # Mostrar estructura de la tabla
        cursor.execute("DESCRIBE ingredientes_completos")
        columnas = cursor.fetchall()
        
        print(f"\n🏗️ Estructura de la tabla (Total: {len(columnas)} columnas):")
        print("-" * 60)
        for col in columnas[:10]:  # Mostrar solo las primeras 10
            print(f"{col['Field']} - {col['Type']} - {col['Null']} - {col['Key']}")
        print("... (y más columnas)")
        
    except Exception as e:
        print(f"❌ Error al verificar la tabla: {e}")
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("🔍 Verificando la tabla ingredientes_completos...")
    verificar_tabla()
