from flask import Blueprint, request, session, jsonify
from app.db import get_db_connection
from functools import wraps
from typing import Any

calculadora_ingredientes_bp = Blueprint('calculadora_ingredientes_bp', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'No autorizado'}), 401
        return f(*args, **kwargs)
    return decorated_function

def safe_float(value, default=0.0):
    """Convierte un valor a float de manera segura"""
    try:
        if value is None:
            return default
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_int(value, default=0):
    """Convierte un valor a entero de manera segura"""
    try:
        if value is None:
            return default
        return int(value)
    except (ValueError, TypeError):
        return default

@calculadora_ingredientes_bp.route('/api/calcular_ingredientes', methods=['POST'])
@login_required
def calcular_ingredientes():
    """API para calcular cantidades de ingredientes según consumo animal"""
    try:
        data = request.get_json()
        formula_id = safe_int(data.get('formula_id'))
        consumo_diario = safe_float(data.get('consumo_diario'))
        numero_animales = safe_int(data.get('numero_animales'))
        dias_produccion = safe_int(data.get('dias_produccion'))
        
        if not formula_id or consumo_diario <= 0 or numero_animales <= 0 or dias_produccion <= 0:
            return jsonify({'error': 'Todos los campos son requeridos y deben ser mayores a 0'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Obtener información de la mezcla
        cursor.execute("""
            SELECT id, nombre, tipo_animales, etapa_produccion
            FROM mezclas 
            WHERE id = %s AND usuario_id = %s
        """, (formula_id, session['user_id']))
        
        mezcla = cursor.fetchone()
        if not mezcla:
            return jsonify({'error': 'Fórmula no encontrada'}), 404
        
        # Obtener ingredientes de la mezcla
        cursor.execute("""
            SELECT mi.inclusion as porcentaje, 
                   i.id, i.nombre, i.precio, i.ms
            FROM mezcla_ingredientes mi
            JOIN ingredientes i ON mi.ingrediente_id = i.id
            WHERE mi.mezcla_id = %s
            ORDER BY mi.inclusion DESC
        """, (formula_id,))
        
        ingredientes = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Calcular totales
        consumo_total_diario = consumo_diario * numero_animales
        consumo_total_periodo = consumo_total_diario * dias_produccion
        
        ingredientes_calculados = []
        costo_total = 0
        
        for ing in ingredientes:
            ing_typed: Any = ing
            porcentaje = safe_float(ing_typed.get('porcentaje', 0))
            precio = safe_float(ing_typed.get('precio', 0))
            
            cantidad_diaria = (consumo_total_diario * porcentaje) / 100
            cantidad_total = (consumo_total_periodo * porcentaje) / 100
            costo_ingrediente = cantidad_total * precio
            
            costo_total += costo_ingrediente
            
            ingredientes_calculados.append({
                'nombre': ing_typed.get('nombre', ''),
                'porcentaje': porcentaje,
                'cantidad_diaria': cantidad_diaria,
                'cantidad_total': cantidad_total,
                'precio': precio,
                'costo_total': costo_ingrediente
            })
        
        # Calcular métricas adicionales
        costo_por_kg = costo_total / consumo_total_periodo if consumo_total_periodo > 0 else 0
        costo_por_animal_dia = (costo_total / numero_animales) / dias_produccion if numero_animales > 0 and dias_produccion > 0 else 0
        
        mezcla_typed: Any = mezcla
        return jsonify({
            'success': True,
            'mezcla': {
                'nombre': mezcla_typed.get('nombre', ''),
                'tipo_animales': mezcla_typed.get('tipo_animales', ''),
                'etapa_produccion': mezcla_typed.get('etapa_produccion', '')
            },
            'parametros': {
                'consumo_diario': consumo_diario,
                'numero_animales': numero_animales,
                'dias_produccion': dias_produccion,
                'consumo_total_diario': consumo_total_diario,
                'consumo_total_periodo': consumo_total_periodo
            },
            'ingredientes': ingredientes_calculados,
            'resumen': {
                'costo_total': costo_total,
                'costo_por_kg': costo_por_kg,
                'costo_por_animal_dia': costo_por_animal_dia
            }
        })
        
    except Exception as e:
        print(f"❌ Error en calculadora de ingredientes: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500
