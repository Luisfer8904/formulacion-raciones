import pandas as pd
import mysql.connector

# Configuración de conexión
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": "3306",
    "database": "db_nutriapp",
    "user": "root",
    "password": "root1234"
}

def import_ingredientes():
    # Leer el archivo Excel
    df = pd.read_excel('Tabla de ingrediente PASAR.xlsx')
    
    # Conectar a la base de datos
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Limpiar tabla existente
    cursor.execute("DELETE FROM ingredientes")
    
    imported_count = 0
    
    for index, row in df.iterrows():
        try:
            # Solo usar las columnas básicas que sabemos que existen
            ingrediente = str(row['INGREDIENTES']).strip() if pd.notna(row['INGREDIENTES']) else f"Ingrediente_{row['ID']}"
            precio = str(row['PRECIO']) if pd.notna(row['PRECIO']) else None
            comentarios = str(row['COMENTARIOS']).strip() if pd.notna(row['COMENTARIOS']) else None
            
            # Valores nutricionales principales usando los nombres correctos
            energia = str(row['EMA_AVES _(Kcal/kg)']) if pd.notna(row['EMA_AVES _(Kcal/kg)']) else None
            proteina = str(row['PB_(%)']) if pd.notna(row['PB_(%)']) else None
            fibra = str(row['FB_(%)']) if pd.notna(row['FB_(%)']) else None
            calcio = str(row['Ca_(%)']) if pd.notna(row['Ca_(%)']) else None
            fosforo = str(row['P_(%)']) if pd.notna(row['P_(%)']) else None
            lisina = str(row['LYS_(%)']) if pd.notna(row['LYS_(%)']) else None
            metionina = str(row['MET_(%)']) if pd.notna(row['MET_(%)']) else None
            
            # Insertar nuevo ingrediente usando solo las columnas básicas
            cursor.execute("""
                INSERT INTO ingredientes (
                    INGREDIENTES, PRECIO, COMENTARIOS
                ) VALUES (%s, %s, %s)
            """, (
                ingrediente, precio, comentarios
            ))
            
            print(f"Insertado: {ingrediente}")
            imported_count += 1
            
        except Exception as e:
            print(f"Error procesando fila {index}: {e}")
            continue
    
    # Confirmar cambios
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\n✅ Proceso completado. {imported_count} ingredientes procesados.")

if __name__ == "__main__":
    import_ingredientes()
