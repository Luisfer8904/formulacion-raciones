import pandas as pd
import mysql.connector
from decimal import Decimal

# Configuración de conexión
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": "3306",
    "database": "db_nutriapp",
    "user": "root",
    "password": "root1234"
}

def to_decimal(value):
    """Convierte valores a decimal válido"""
    try:
        if pd.isna(value) or str(value).strip() == '' or str(value).lower() == 'nan':
            return None
        val = float(str(value).strip())
        return round(val, 4)
    except (ValueError, TypeError):
        return None

def import_ingredientes():
    # Leer el archivo Excel
    df = pd.read_excel('Tabla de ingrediente PASAR.xlsx')
    
    # Conectar a la base de datos
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Limpiar tabla existente (opcional)
    # cursor.execute("DELETE FROM ingredientes")
    
    imported_count = 0
    
    for index, row in df.iterrows():
        try:
            # Mapear columnas del Excel a la base de datos
            nombre = str(row['INGREDIENTES']).strip() if pd.notna(row['INGREDIENTES']) else f"Ingrediente_{row['ID']}"
            precio_lps = to_decimal(row['PRECIO'])
            descripcion = str(row['COMENTARIOS']).strip() if pd.notna(row['COMENTARIOS']) else None
            
            # Valores nutricionales principales
            energia_kcal = to_decimal(row.get('EM_AVES _(Kcal/kg)', None))
            proteina = to_decimal(row.get('PB_(%)', None))
            fibra = to_decimal(row.get('FB_(%)', None))
            calcio = to_decimal(row.get('Ca_(%)', None))
            fosforo = to_decimal(row.get('P_(%)', None))
            lisina = to_decimal(row.get('LYS_(%)', None))
            metionina = to_decimal(row.get('MET_(%)', None))
            
            # Verificar si el ingrediente ya existe
            cursor.execute("SELECT id FROM ingredientes WHERE nombre = %s", (nombre,))
            existing = cursor.fetchone()
            
            if existing:
                # Actualizar ingrediente existente
                cursor.execute("""
                    UPDATE ingredientes SET
                        precio_lps=%s, descripcion=%s, energia_kcal=%s, proteina=%s, 
                        fibra=%s, calcio=%s, fosforo=%s, lisina=%s, metionina=%s
                    WHERE nombre=%s
                """, (
                    precio_lps, descripcion, energia_kcal, proteina, fibra,
                    calcio, fosforo, lisina, metionina, nombre
                ))
                print(f"Actualizado: {nombre}")
            else:
                # Insertar nuevo ingrediente
                cursor.execute("""
                    INSERT INTO ingredientes (
                        nombre, descripcion, tipo, energia_kcal, proteina, fibra,
                        calcio, fosforo, lisina, metionina, precio_lps, unidad_precio, fecha_creacion
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                """, (
                    nombre, descripcion, 'Importado', energia_kcal, proteina, fibra,
                    calcio, fosforo, lisina, metionina, precio_lps, 'kg'
                ))
                print(f"Insertado: {nombre}")
            
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
