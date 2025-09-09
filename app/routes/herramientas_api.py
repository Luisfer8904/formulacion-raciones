from flask import Blueprint, request, jsonify, session, redirect, url_for
from functools import wraps
from app.db import get_db_connection
from typing import Any, Dict, List, Optional

herramientas_api_bp = Blueprint('herramientas_api_bp', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'No autorizado'}), 401
        return f(*args, **kwargs)
    return decorated_function

@herramientas_api_bp.route('/api/convertir_unidades', methods=['POST'])
@login_required
def convertir_unidades():
    """API para conversión de unidades"""
    try:
        data = request.get_json()
        valor = float(data.get('valor', 0))
        origen = data.get('origen', '')
        destino = data.get('destino', '')
        
        if valor == 0:
            return jsonify({
                'success': False,
                'error': 'El valor debe ser mayor a 0'
            }), 400
        
        # Factores de conversión
        conversiones = {
            'kg': {
                'g': 1000,
                'lb': 2.20462,
                'oz': 35.274,
                'ton': 0.001
            },
            'g': {
                'kg': 0.001,
                'lb': 0.00220462,
                'oz': 0.035274,
                'ton': 0.000001
            },
            'lb': {
                'kg': 0.453592,
                'g': 453.592,
                'oz': 16,
                'ton': 0.000453592
            },
            'oz': {
                'kg': 0.0283495,
                'g': 28.3495,
                'lb': 0.0625,
                'ton': 0.0000283495
            },
            'ton': {
                'kg': 1000,
                'g': 1000000,
                'lb': 2204.62,
                'oz': 35274
            }
        }
        
        if origen not in conversiones or destino not in conversiones[origen]:
            return jsonify({
                'success': False,
                'error': 'Conversión no soportada'
            }), 400
        
        if origen == destino:
            resultado = valor
        else:
            resultado = valor * conversiones[origen][destino]
        
        return jsonify({
            'success': True,
            'resultado': round(resultado, 6),
            'mensaje': f'{valor} {origen} = {round(resultado, 6)} {destino}'
        })
        
    except Exception as e:
        print(f"❌ Error en conversión de unidades: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@herramientas_api_bp.route('/api/calcular_nutriente', methods=['POST'])
@login_required
def calcular_nutriente():
    """API para cálculo de nutrientes con materia seca"""
    try:
        data = request.get_json()
        porcentaje_nutriente = float(data.get('porcentaje_nutriente', 0))
        materia_seca = float(data.get('materia_seca', 100))
        cantidad = float(data.get('cantidad', 0))
        tipo_nutriente = data.get('tipo_nutriente', 'proteina')
        
        if cantidad <= 0:
            return jsonify({
                'success': False,
                'error': 'La cantidad debe ser mayor a 0'
            }), 400
        
        if materia_seca <= 0 or materia_seca > 100:
            return jsonify({
                'success': False,
                'error': 'La materia seca debe estar entre 0.1 y 100'
            }), 400
        
        # Cálculo: Cantidad * %MS * %Nutriente
        cantidad_ms = cantidad * (materia_seca / 100)
        
        if tipo_nutriente == 'energia':
            # Para energía no se divide por 100
            nutriente_total = cantidad_ms * porcentaje_nutriente
            unidad = 'Mcal'
        else:
            nutriente_total = cantidad_ms * (porcentaje_nutriente / 100)
            unidad = 'kg'
        
        nombres_nutrientes = {
            'proteina': 'Proteína Cruda',
            'grasa': 'Grasa Cruda',
            'fibra': 'Fibra Cruda',
            'cenizas': 'Cenizas',
            'carbohidratos': 'Carbohidratos',
            'energia': 'Energía Metabolizable'
        }
        
        nombre_nutriente = nombres_nutrientes.get(tipo_nutriente, 'Nutriente')
        
        return jsonify({
            'success': True,
            'resultado': round(nutriente_total, 4),
            'unidad': unidad,
            'nombre_nutriente': nombre_nutriente,
            'cantidad_ms': round(cantidad_ms, 4),
            'calculo': {
                'paso1': f'{cantidad} kg × {materia_seca}% = {round(cantidad_ms, 4)} kg MS',
                'paso2': f'{round(cantidad_ms, 4)} kg × {porcentaje_nutriente}{"%" if tipo_nutriente != "energia" else " Mcal/kg"} = {round(nutriente_total, 4)} {unidad}'
            }
        })
        
    except Exception as e:
        print(f"❌ Error en cálculo de nutriente: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@herramientas_api_bp.route('/api/calcular_aportes_nutricionales', methods=['POST'])
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
            
            nombre_ingrediente = datos_ingrediente[0]['nombre']
            ms = float(datos_ingrediente[0]['ms'] or 100)
            
            detalle_ingrediente = {
                'nombre': nombre_ingrediente,
                'inclusion': inclusion,
                'ms': ms,
                'nutrientes': {}
            }
            
            for dato in datos_ingrediente:
                if dato['nutriente_nombre'] and dato['valor']:
                    nutriente = dato['nutriente_nombre']
                    valor_base = float(dato['valor'])
                    
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

@herramientas_api_bp.route('/api/ingredientes_con_limites', methods=['GET'])
@login_required
def obtener_ingredientes_con_limites():
    """API para obtener ingredientes con sus límites de inclusión"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar si las columnas de límites existen
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'ingredientes'
            AND COLUMN_NAME IN ('limite_min', 'limite_max')
        """)
        
        columnas_limites = cursor.fetchall()
        tiene_limites = len(columnas_limites) == 2
        
        if tiene_limites:
            # Consulta con límites
            cursor.execute("""
                SELECT id, nombre, comentario, ms, precio, 
                       COALESCE(limite_min, 0.00) as limite_min,
                       COALESCE(limite_max, 100.00) as limite_max
                FROM ingredientes 
                WHERE usuario_id = %s 
                ORDER BY nombre ASC
            """, (session['user_id'],))
        else:
            # Consulta sin límites (valores por defecto)
            cursor.execute("""
                SELECT id, nombre, comentario, ms, precio,
                       0.00 as limite_min,
                       100.00 as limite_max
                FROM ingredientes 
                WHERE usuario_id = %s 
                ORDER BY nombre ASC
            """, (session['user_id'],))
        
        ingredientes = cursor.fetchall()
        
        # Obtener nutrientes para cada ingrediente
        for ingrediente in ingredientes:
            cursor.execute("""
                SELECT n.id, n.nombre, n.unidad, inut.valor
                FROM nutrientes n
                LEFT JOIN ingredientes_nutrientes inut ON n.id = inut.nutriente_id 
                    AND inut.ingrediente_id = %s
                WHERE n.usuario_id = %s
                ORDER BY n.nombre ASC
            """, (ingrediente['id'], session['user_id']))
            
            nutrientes = cursor.fetchall()
            ingrediente['nutrientes'] = nutrientes or []
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'ingredientes': ingredientes,
            'tiene_limites': tiene_limites
        })
        
    except Exception as e:
        print(f"❌ Error al obtener ingredientes con límites: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@herramientas_api_bp.route('/api/actualizar_limites_ingrediente', methods=['POST'])
@login_required
def actualizar_limites_ingrediente():
    """API para actualizar límites de un ingrediente"""
    try:
        data = request.get_json()
        ingrediente_id = data.get('ingrediente_id')
        limite_min = float(data.get('limite_min', 0))
        limite_max = float(data.get('limite_max', 100))
        
        if not ingrediente_id:
            return jsonify({
                'success': False,
                'error': 'ID de ingrediente requerido'
            }), 400
        
        if limite_min < 0 or limite_min > 100:
            return jsonify({
                'success': False,
                'error': 'El límite mínimo debe estar entre 0 y 100'
            }), 400
        
        if limite_max < 0 or limite_max > 100:
            return jsonify({
                'success': False,
                'error': 'El límite máximo debe estar entre 0 y 100'
            }), 400
        
        if limite_min > limite_max:
            return jsonify({
                'success': False,
                'error': 'El límite mínimo no puede ser mayor al máximo'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar que el ingrediente pertenece al usuario
        cursor.execute("""
            SELECT id FROM ingredientes 
            WHERE id = %s AND usuario_id = %s
        """, (ingrediente_id, session['user_id']))
        
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Ingrediente no encontrado'
            }), 404
        
        # Actualizar límites
        cursor.execute("""
            UPDATE ingredientes 
            SET limite_min = %s, limite_max = %s 
            WHERE id = %s AND usuario_id = %s
        """, (limite_min, limite_max, ingrediente_id, session['user_id']))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'mensaje': 'Límites actualizados correctamente'
        })
        
    except Exception as e:
        print(f"❌ Error al actualizar límites: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500
