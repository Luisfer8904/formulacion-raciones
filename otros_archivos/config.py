import mysql.connector

# Configuración de la base de datos
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": "3306",
    "database": "formulacion_nutricional",
    "user": "root",
    "password": "root1234"
}

def get_db_connection():
    """Obtiene una conexión a la base de datos"""
    return mysql.connector.connect(**DB_CONFIG)

def to_decimal(value):
    """Convierte valores a decimales válidos"""
    try:
        if not value or str(value).strip() == '':
            return None
        val = float(value.strip())
        return round(val, 4)
    except (ValueError, TypeError):
        return None
