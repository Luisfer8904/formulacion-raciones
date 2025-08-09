import mysql.connector

# Configuración de conexión
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": "3306",
    "database": "db_nutriapp",
    "user": "root",
    "password": "root1234"
}

def actualizar_columnas():
    """Actualizar las columnas para permitir valores más grandes"""
    
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Modificar las columnas para permitir valores más grandes
    alter_statements = [
        "ALTER TABLE ingredientes_completos MODIFY Cu_ppm DECIMAL(12,4)",
        "ALTER TABLE ingredientes_completos MODIFY Fe_ppm DECIMAL(12,4)",
        "ALTER TABLE ingredientes_completos MODIFY Zn_ppm DECIMAL(12,4)",
        "ALTER TABLE ingredientes_completos MODIFY Mn_ppm DECIMAL(12,4)",
        "ALTER TABLE ingredientes_completos MODIFY Colina_ppm DECIMAL(12,4)",
        "ALTER TABLE ingredientes_completos MODIFY Vit_E_ppm DECIMAL(12,4)",
        "ALTER TABLE ingredientes_completos MODIFY Biotina_ppm DECIMAL(12,4)"
    ]
    
    try:
        for statement in alter_statements:
            cursor.execute(statement)
            print(f"✅ Ejecutado: {statement}")
        
        conn.commit()
        print("\n✅ Columnas actualizadas exitosamente")
        
    except Exception as e:
        print(f"\n❌ Error al actualizar columnas: {e}")
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("🔄 Actualizando columnas para permitir valores más grandes...")
    actualizar_columnas()
