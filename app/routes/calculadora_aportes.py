from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
from app.db import get_db_connection
from datetime import datetime

calculadora_aportes_bp = Blueprint('calculadora_aportes_bp', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth_bp.login'))
        return f(*args, **kwargs)
    return decorated_function

@calculadora_aportes_bp.route('/api/obtener_ingredientes', methods=['GET'])
@login_required
def obtener_ingredientes():
    """API para obtener lista de ingredientes disponibles"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, nombre, precio_kg, materia_seca
            FROM ingredientes 
            WHERE usuario_id = %s
            ORDER BY nombre
        """, (session['user_id'],))
        
        ingredientes = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'ingredientes': ingredientes
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@calculadora_aportes_bp.route('/api/obtener_nutrientes', methods=['GET'])
@login_required
def obtener_nutrientes():
    """API para obtener lista de nutrientes disponibles"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, nombre, unidad
            FROM nutrientes 
            WHERE usuario_id = %s
            ORDER BY nombre
        """, (session['user_id'],))
        
        nutrientes = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'nutrientes': nutrientes
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@calculadora_aportes_bp.route('/api/obtener_valores_nutricionales', methods=['POST'])
@login_required
def obtener_valores_nutricionales():
    """API para obtener valores nutricionales de un ingrediente específico"""
    try:
        data = request.get_json()
        ingrediente_id = data.get('ingrediente_id')
        nutriente_id = data.get('nutriente_id')
        
        if not ingrediente_id or not nutriente_id:
            return jsonify({
                'success': False,
                'error': 'Se requiere ingrediente_id y nutriente_id'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Obtener el valor nutricional específico
        cursor.execute("""
            SELECT vn.valor, n.nombre as nutriente_nombre, n.unidad,
                   i.nombre as ingrediente_nombre
            FROM ingredientes_nutrientes vn
            JOIN nutrientes n ON vn.nutriente_id = n.id
            JOIN ingredientes i ON vn.ingrediente_id = i.id
            WHERE vn.ingrediente_id = %s AND vn.nutriente_id = %s
        """, (ingrediente_id, nutriente_id))
        
        resultado = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if resultado:
            return jsonify({
                'success': True,
                'valor': resultado['valor'],
                'nutriente': resultado['nutriente_nombre'],
                'unidad': resultado['unidad'],
                'ingrediente': resultado['ingrediente_nombre']
            })
        else:
            return jsonify({
                'success': True,
                'valor': 0,
                'mensaje': 'No se encontró valor nutricional para esta combinación'
            })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@calculadora_aportes_bp.route('/api/calcular_aportes_nutricionales', methods=['POST'])
@login_required
def calcular_aportes_nutricionales():
    """API para calcular aportes nutricionales de una fórmula"""
    try:
        data = request.get_json()
        nombre_formula = data.get('nombre_formula', 'Fórmula sin nombre')
        consumo_animal = float(data.get('consumo_animal', 0))
        ingredientes = data.get('ingredientes', [])
        nutrientes_seleccionados = data.get('nutrientes_seleccionados', [])
        
        if consumo_animal <= 0:
            return jsonify({
                'success': False,
                'error': 'El consumo por animal debe ser mayor a 0'
            }), 400
        
        if not ingredientes:
            return jsonify({
                'success': False,
                'error': 'Debe agregar al menos un ingrediente'
            }), 400
        
        if not nutrientes_seleccionados:
            return jsonify({
                'success': False,
                'error': 'Debe seleccionar al menos un nutriente'
            }), 400
        
        # Validar que la suma de porcentajes sea 100%
        total_porcentaje = sum(float(ing.get('porcentaje', 0)) for ing in ingredientes)
        if abs(total_porcentaje - 100) > 0.1:
            return jsonify({
                'success': False,
                'error': f'La suma de porcentajes debe ser 100%. Actual: {total_porcentaje}%'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        resultados = []
        
        # Para cada nutriente seleccionado, calcular el aporte total
        for nutriente_id in nutrientes_seleccionados:
            # Obtener información del nutriente
            cursor.execute("""
                SELECT nombre, unidad FROM nutrientes WHERE id = %s
            """, (nutriente_id,))
            
            nutriente_info = cursor.fetchone()
            if not nutriente_info:
                continue
            
            aporte_total = 0
            detalle_ingredientes = []
            
            # Para cada ingrediente, obtener su aporte del nutriente
            for ingrediente in ingredientes:
                ingrediente_id = ingrediente.get('id')
                porcentaje = float(ingrediente.get('porcentaje', 0))
                
                # Obtener valor nutricional
                cursor.execute("""
                    SELECT vn.valor, i.nombre as ingrediente_nombre
                    FROM ingredientes_nutrientes vn
                    JOIN ingredientes i ON vn.ingrediente_id = i.id
                    WHERE vn.ingrediente_id = %s AND vn.nutriente_id = %s
                """, (ingrediente_id, nutriente_id))
                
                valor_resultado = cursor.fetchone()
                valor_nutricional = float(valor_resultado['valor']) if valor_resultado and valor_resultado['valor'] else 0
                ingrediente_nombre = valor_resultado['ingrediente_nombre'] if valor_resultado else f"Ingrediente {ingrediente_id}"
                
                # Calcular aporte del ingrediente
                aporte_ingrediente = (porcentaje / 100) * valor_nutricional
                aporte_total += aporte_ingrediente
                
                # Calcular consumo diario del nutriente por este ingrediente
                consumo_diario_ingrediente = (consumo_animal * porcentaje / 100) * (valor_nutricional / 100)
                
                detalle_ingredientes.append({
                    'nombre': ingrediente_nombre,
                    'porcentaje': porcentaje,
                    'valor_nutricional': valor_nutricional,
                    'aporte': round(aporte_ingrediente, 4),
                    'consumo_diario': round(consumo_diario_ingrediente, 4)
                })
            
            # Calcular consumo diario total del nutriente
            consumo_diario_total = (consumo_animal * aporte_total / 100)
            
            resultados.append({
                'nutriente_id': nutriente_id,
                'nutriente_nombre': nutriente_info['nombre'],
                'unidad': nutriente_info['unidad'],
                'aporte_total': round(aporte_total, 4),
                'consumo_diario_total': round(consumo_diario_total, 4),
                'detalle_ingredientes': detalle_ingredientes
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'nombre_formula': nombre_formula,
            'consumo_animal': consumo_animal,
            'total_ingredientes': len(ingredientes),
            'total_nutrientes': len(nutrientes_seleccionados),
            'resultados': resultados
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@calculadora_aportes_bp.route('/api/obtener_mezclas', methods=['GET'])
@login_required
def obtener_mezclas():
    """API para obtener lista de mezclas/fórmulas del usuario"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, nombre, tipo_animales, etapa_produccion, fecha_creacion
            FROM mezclas 
            WHERE usuario_id = %s
            ORDER BY fecha_creacion DESC
        """, (session['user_id'],))
        
        mezclas = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'mezclas': mezclas
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@calculadora_aportes_bp.route('/api/obtener_detalle_mezcla/<int:mezcla_id>', methods=['GET'])
@login_required
def obtener_detalle_mezcla(mezcla_id):
    """API para obtener detalles de una mezcla específica"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Obtener información de la mezcla
        cursor.execute("""
            SELECT id, nombre, tipo_animales, etapa_produccion, observaciones
            FROM mezclas 
            WHERE id = %s AND usuario_id = %s
        """, (mezcla_id, session['user_id']))
        
        mezcla = cursor.fetchone()
        
        if not mezcla:
            return jsonify({
                'success': False,
                'error': 'Mezcla no encontrada'
            }), 404
        
        # Obtener ingredientes de la mezcla
        cursor.execute("""
            SELECT mi.ingrediente_id, mi.inclusion as porcentaje, i.nombre
            FROM mezcla_ingredientes mi
            JOIN ingredientes i ON mi.ingrediente_id = i.id
            WHERE mi.mezcla_id = %s
        """, (mezcla_id,))
        
        ingredientes = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'mezcla': mezcla,
            'ingredientes': ingredientes
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@calculadora_aportes_bp.route('/imprimir_aportes')
@login_required
def imprimir_aportes():
    """Página de impresión para aportes nutricionales"""
    # Obtener datos de la sesión o parámetros
    nombre_formula = request.args.get('nombre_formula', 'Fórmula sin nombre')
    consumo_animal = request.args.get('consumo_animal', '0')
    total_ingredientes = request.args.get('total_ingredientes', '0')
    total_nutrientes = request.args.get('total_nutrientes', '0')
    
    # Para una implementación completa, aquí se obtendrían los resultados
    # desde la base de datos o se pasarían como parámetros
    resultados = []  # Esto se llenaría con los datos reales
    
    return render_template('operaciones/imprimir_aportes.html',
                         nombre_formula=nombre_formula,
                         consumo_animal=consumo_animal,
                         total_ingredientes=total_ingredientes,
                         total_nutrientes=total_nutrientes,
                         resultados=resultados,
                         fecha_actual=datetime.now().strftime('%d/%m/%Y %H:%M'))
