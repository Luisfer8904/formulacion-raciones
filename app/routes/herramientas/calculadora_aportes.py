from flask import Blueprint, request, jsonify, session
from functools import wraps
from app.db import get_db_connection

calculadora_aportes_bp = Blueprint('calculadora_aportes_bp', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'No autorizado'}), 401
        return f(*args, **kwargs)
    return decorated_function

@calculadora_aportes_bp.route('/api/calcular_aportes_nutricionales', methods=['POST'])
@login_required
def calcular_aportes_nutricionales():
    """API para cálculo de aportes nutricionales de una fórmula"""
    try:
        data = request.get_json()
        ingredientes = data.get('ingredientes', [])
        consumo = float(data.get('consumo', 3.0))
        tipo_calculo = data.get('tipo_calculo', 'base_humeda')  # base_humeda o base_seca
        
        if not ingredientes:
            return jsonify({
                'success': False,
                'error': 'Se requiere al menos un ingrediente'
            }), 400
        
        if consumo <= 0:
            return jsonify({
                'success': False,
                'error': 'El consumo debe ser mayor a 0'
            }), 400
        
        # Obtener datos de ingredientes de la base de datos
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        aportes_totales = {}
        detalles_calculo = []
        
        for ing_data in ingredientes:
            ingrediente_id = ing_data.get('id')
            inclusion = float(ing_data.get('inclusion', 0))
            
            if inclusion <= 0:
                continue
            
            # Obtener datos del ingrediente
            cursor.execute("""
                SELECT i.nombre, i.ms,
                       n.nombre as nutriente_nombre, inut.valor
                FROM ingredientes i
                LEFT JOIN ingredientes_nutrientes inut ON i.id = inut.ingrediente_id
                LEFT JOIN nutrientes n ON inut.nutriente_id = n.id
                WHERE i.id = %s AND i.usuario_id = %s
            """, (ingrediente_id, session['user_id']))
            
            datos_ingrediente = cursor.fetchall()
            
            if not datos_ingrediente:
                continue
            
            # Obtener datos básicos del ingrediente
            nombre_ingrediente = str(datos_ingrediente[0].get('nombre', ''))
            ms_value = datos_ingrediente[0].get('ms')
            ms = float(ms_value) if ms_value is not None else 100.0
            
            detalle_ingrediente = {
                'nombre': nombre_ingrediente,
                'inclusion': inclusion,
                'ms': ms,
                'nutrientes': {}
            }
            
            for dato in datos_ingrediente:
                nutriente_nombre = dato.get('nutriente_nombre')
                valor_raw = dato.get('valor')
                
                if nutriente_nombre and valor_raw is not None:
                    nutriente = str(nutriente_nombre)
                    valor_base = float(valor_raw)
                    
                    # Calcular aporte según tipo de cálculo
                    if tipo_calculo == 'base_seca':
                        aporte = (inclusion / 100) * valor_base * (ms / 100) * consumo / 100
                    else:
                        aporte = (inclusion / 100) * valor_base * consumo / 100
                    
                    if nutriente not in aportes_totales:
                        aportes_totales[nutriente] = 0
                    
                    aportes_totales[nutriente] += aporte
                    detalle_ingrediente['nutrientes'][nutriente] = round(aporte, 4)
            
            detalles_calculo.append(detalle_ingrediente)
        
        cursor.close()
        conn.close()
        
        # Redondear aportes totales
        for nutriente in aportes_totales:
            aportes_totales[nutriente] = round(aportes_totales[nutriente], 4)
        
        return jsonify({
            'success': True,
            'aportes_totales': aportes_totales,
            'detalles_calculo': detalles_calculo,
            'consumo': consumo,
            'tipo_calculo': tipo_calculo
        })
        
    except Exception as e:
        print(f"❌ Error en cálculo de aportes: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@calculadora_aportes_bp.route('/api/calcular_aporte_simple', methods=['POST'])
@login_required
def calcular_aporte_simple():
    """API para cálculo simple de aporte nutricional"""
    try:
        data = request.get_json()
        consumo = float(data.get('consumo', 3.0))
        materia_seca = float(data.get('materia_seca', 88.0))
        porcentaje_nutriente = float(data.get('porcentaje_nutriente', 22.0))
        
        if consumo <= 0:
            return jsonify({
                'success': False,
                'error': 'El consumo debe ser mayor a 0'
            }), 400
        
        if materia_seca <= 0 or materia_seca > 100:
            return jsonify({
                'success': False,
                'error': 'La materia seca debe estar entre 0.1 y 100'
            }), 400
        
        # Cálculo paso a paso
        consumo_ms = consumo * (materia_seca / 100)
        aporte_nutriente = consumo_ms * (porcentaje_nutriente / 100)
        
        return jsonify({
            'success': True,
            'resultado': round(aporte_nutriente, 4),
            'consumo_ms': round(consumo_ms, 4),
            'calculo': {
                'paso1': f'Consumo MS: {consumo} kg × {materia_seca}% = {round(consumo_ms, 4)} kg',
                'paso2': f'Aporte: {round(consumo_ms, 4)} kg × {porcentaje_nutriente}% = {round(aporte_nutriente, 4)} kg'
            },
            'datos_entrada': {
                'consumo': consumo,
                'materia_seca': materia_seca,
                'porcentaje_nutriente': porcentaje_nutriente
            }
        })
        
    except Exception as e:
        print(f"❌ Error en cálculo simple: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500
