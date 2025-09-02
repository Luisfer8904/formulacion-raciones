from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
from app.db import get_db_connection
from datetime import datetime

calculadora_aportes_nueva_bp = Blueprint('calculadora_aportes_nueva_bp', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth_bp.login'))
        return f(*args, **kwargs)
    return decorated_function

@calculadora_aportes_nueva_bp.route('/api/obtener_mezclas_para_aportes', methods=['GET'])
@login_required
def obtener_mezclas_para_aportes():
    """API para obtener lista de mezclas/fórmulas del usuario"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT m.id, m.nombre, m.tipo_animales, m.etapa_produccion, m.fecha_creacion,
                   COUNT(mi.ingrediente_id) as total_ingredientes
            FROM mezclas m
            LEFT JOIN mezcla_ingredientes mi ON m.id = mi.mezcla_id
            WHERE m.usuario_id = %s
            GROUP BY m.id, m.nombre, m.tipo_animales, m.etapa_produccion, m.fecha_creacion
            HAVING total_ingredientes > 0
            ORDER BY m.fecha_creacion DESC
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

@calculadora_aportes_nueva_bp.route('/api/obtener_ingredientes_de_mezcla/<int:mezcla_id>', methods=['GET'])
@login_required
def obtener_ingredientes_de_mezcla(mezcla_id):
    """API para obtener ingredientes de una mezcla específica"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que la mezcla pertenece al usuario
        cursor.execute("""
            SELECT nombre FROM mezclas 
            WHERE id = %s AND usuario_id = %s
        """, (mezcla_id, session['user_id']))
        
        mezcla = cursor.fetchone()
        if not mezcla:
            return jsonify({
                'success': False,
                'error': 'Mezcla no encontrada'
            }), 404
        
        # Obtener ingredientes de la mezcla con materia seca
        cursor.execute("""
            SELECT mi.ingrediente_id, mi.inclusion as porcentaje, i.nombre, i.ms as materia_seca_ingrediente
            FROM mezcla_ingredientes mi
            JOIN ingredientes i ON mi.ingrediente_id = i.id
            WHERE mi.mezcla_id = %s
            ORDER BY mi.inclusion DESC
        """, (mezcla_id,))
        
        ingredientes = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'mezcla_nombre': mezcla['nombre'],
            'ingredientes': ingredientes
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@calculadora_aportes_nueva_bp.route('/api/obtener_nutrientes_para_aportes', methods=['GET'])
@login_required
def obtener_nutrientes_para_aportes():
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

@calculadora_aportes_nueva_bp.route('/api/calcular_aportes_completo', methods=['POST'])
@login_required
def calcular_aportes_completo():
    """API para calcular aportes nutricionales completos con materia seca"""
    try:
        data = request.get_json()
        mezcla_id = data.get('mezcla_id')
        consumo_animal = float(data.get('consumo_animal', 0))
        nutrientes_seleccionados = data.get('nutrientes_seleccionados', [])
        
        if consumo_animal <= 0:
            return jsonify({
                'success': False,
                'error': 'El consumo por animal debe ser mayor a 0'
            }), 400
        
        if not mezcla_id:
            return jsonify({
                'success': False,
                'error': 'Debe seleccionar una fórmula'
            }), 400
        
        if not nutrientes_seleccionados:
            return jsonify({
                'success': False,
                'error': 'Debe seleccionar al menos un nutriente'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Obtener información de la mezcla
        cursor.execute("""
            SELECT nombre, tipo_animales, etapa_produccion
            FROM mezclas 
            WHERE id = %s AND usuario_id = %s
        """, (mezcla_id, session['user_id']))
        
        mezcla = cursor.fetchone()
        if not mezcla:
            return jsonify({
                'success': False,
                'error': 'Fórmula no encontrada'
            }), 404
        
        # Obtener ingredientes de la mezcla con su materia seca
        cursor.execute("""
            SELECT mi.ingrediente_id, mi.inclusion as porcentaje, i.nombre, i.ms as materia_seca_ingrediente
            FROM mezcla_ingredientes mi
            JOIN ingredientes i ON mi.ingrediente_id = i.id
            WHERE mi.mezcla_id = %s
        """, (mezcla_id,))
        
        ingredientes_mezcla = cursor.fetchall()
        
        if not ingredientes_mezcla:
            return jsonify({
                'success': False,
                'error': 'La fórmula no tiene ingredientes'
            }), 400
        
        # Primero calcular la materia seca promedio ponderada de la dieta
        materia_seca_dieta_calculada = 0
        for ingrediente in ingredientes_mezcla:
            porcentaje_en_formula = float(ingrediente['porcentaje'])
            ms_ingrediente = float(ingrediente['materia_seca_ingrediente']) if ingrediente['materia_seca_ingrediente'] else 88.0
            materia_seca_dieta_calculada += (porcentaje_en_formula / 100) * ms_ingrediente
        
        resultados = []
        
        # Para cada nutriente seleccionado, calcular el aporte total
        for nutriente_id in nutrientes_seleccionados:
            # Obtener información del nutriente
            cursor.execute("""
                SELECT nombre, unidad FROM nutrientes 
                WHERE id = %s AND usuario_id = %s
            """, (nutriente_id, session['user_id']))
            
            nutriente_info = cursor.fetchone()
            if not nutriente_info:
                continue
            
            aporte_total_porcentaje = 0
            detalle_ingredientes = []
            consumo_nutriente_total = 0
            
            # Para cada ingrediente, obtener su aporte del nutriente
            for ingrediente in ingredientes_mezcla:
                ingrediente_id = ingrediente['ingrediente_id']
                porcentaje_en_formula = float(ingrediente['porcentaje'])
                ingrediente_nombre = ingrediente['nombre']
                ms_ingrediente = float(ingrediente['materia_seca_ingrediente']) if ingrediente['materia_seca_ingrediente'] else 88.0
                
                # Obtener valor nutricional del ingrediente para este nutriente
                cursor.execute("""
                    SELECT valor
                    FROM ingredientes_nutrientes
                    WHERE ingrediente_id = %s AND nutriente_id = %s
                """, (ingrediente_id, nutriente_id))
                
                valor_resultado = cursor.fetchone()
                valor_nutricional = float(valor_resultado['valor']) if valor_resultado and valor_resultado['valor'] else 0
                
                # Calcular aporte del ingrediente al nutriente total de la dieta
                aporte_ingrediente = (porcentaje_en_formula / 100) * valor_nutricional
                aporte_total_porcentaje += aporte_ingrediente
                
                # Calcular consumo de nutriente por ingrediente: Consumo × %Ingrediente × %MS_ingrediente × %Nutriente
                consumo_ingrediente = consumo_animal * (porcentaje_en_formula / 100)
                consumo_ms_ingrediente = consumo_ingrediente * (ms_ingrediente / 100)
                consumo_nutriente_ingrediente = consumo_ms_ingrediente * (valor_nutricional / 100)
                consumo_nutriente_total += consumo_nutriente_ingrediente
                
                detalle_ingredientes.append({
                    'nombre': ingrediente_nombre,
                    'porcentaje_en_formula': porcentaje_en_formula,
                    'ms_ingrediente': ms_ingrediente,
                    'valor_nutricional': valor_nutricional,
                    'aporte_al_nutriente': round(aporte_ingrediente, 4),
                    'consumo_ingrediente': round(consumo_ingrediente, 4),
                    'consumo_ms_ingrediente': round(consumo_ms_ingrediente, 4),
                    'consumo_nutriente_ingrediente': round(consumo_nutriente_ingrediente, 4)
                })
            
            # Cálculo con materia seca calculada de la dieta
            consumo_ms_dieta = consumo_animal * (materia_seca_dieta_calculada / 100)
            
            resultados.append({
                'nutriente_id': nutriente_id,
                'nutriente_nombre': nutriente_info['nombre'],
                'unidad': nutriente_info['unidad'],
                'aporte_total_porcentaje': round(aporte_total_porcentaje, 4),
                'materia_seca_dieta_calculada': round(materia_seca_dieta_calculada, 2),
                'consumo_ms_dieta': round(consumo_ms_dieta, 4),
                'consumo_nutriente_total': round(consumo_nutriente_total, 4),
                'detalle_ingredientes': detalle_ingredientes,
                'calculo_paso_a_paso': [
                    f'1. MS Dieta (ponderada): {round(materia_seca_dieta_calculada, 2)}%',
                    f'2. Consumo MS Dieta: {consumo_animal} kg × {round(materia_seca_dieta_calculada, 2)}% = {round(consumo_ms_dieta, 4)} kg',
                    f'3. {nutriente_info["nombre"]} Total: {round(consumo_nutriente_total, 4)} {nutriente_info["unidad"]} (suma por ingrediente)'
                ]
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'mezcla': mezcla,
            'consumo_animal': consumo_animal,
            'materia_seca_dieta_calculada': materia_seca_dieta_calculada,
            'total_ingredientes': len(ingredientes_mezcla),
            'total_nutrientes': len(nutrientes_seleccionados),
            'resultados': resultados
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
