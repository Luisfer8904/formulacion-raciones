import mysql.connector
import re
import os
from typing import List, Optional, Any, Tuple

# Configuración de conexión a la base de datos
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "127.0.0.1"),
    "port": os.environ.get("DB_PORT", "3306"),
    "database": os.environ.get("DB_DATABASE", "formulacion_nutricional"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", "root1234")
}

def get_db_connection():
    """Obtiene una conexión a la base de datos MySQL"""
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

def obtener_nutrientes_disponibles() -> List[str]:
    """Obtiene los nutrientes disponibles desde la base de datos"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM nutrientes")
    resultados: Any = cursor.fetchall()
    cursor.close()
    conn.close()

    nutrientes = []
    for resultado in resultados:
        nutrientes.append(resultado[0])
    return nutrientes
