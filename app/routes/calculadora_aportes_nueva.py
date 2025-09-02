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
        
        # Obtener ingredientes de la mezcla
        cursor.execute("""
            SELECT mi.ingrediente_id, mi.inclusion as porcentaje, i.nombre
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
        
        # Obtener ingredientes de la mezcla con materia seca para calcular valores BS
        cursor.execute("""
            SELECT mi.ingrediente_id, mi.inclusion as porcentaje, i.nombre, i.ms
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
            
            cantidad_total_dieta = 0
            detalle_ingredientes = []
            aporte_total_final = 0
            unidad_final = nutriente_info['unidad']
            
            # Para cada ingrediente, obtener su aporte del nutriente (usando valores BS)
            for ingrediente in ingredientes_mezcla:
                ingrediente_id = ingrediente['ingrediente_id']
                porcentaje_en_formula = float(ingrediente['porcentaje'])
                ingrediente_nombre = ingrediente['nombre']
                
                # Obtener valor nutricional TC del ingrediente para este nutriente
                cursor.execute("""
                    SELECT valor
                    FROM ingredientes_nutrientes
                    WHERE ingrediente_id = %s AND nutriente_id = %s
                """, (ingrediente_id, nutriente_id))
                
                valor_resultado = cursor.fetchone()
                valor_tc = float(valor_resultado['valor']) if valor_resultado and valor_resultado['valor'] else 0
                
                # Obtener materia seca del ingrediente
                ms_ingrediente = float(ingrediente.get('ms', 100))
                
                # Calcular valor BS: valor_tc * (ms / 100)
                valor_bs = valor_tc * (ms_ingrediente / 100)
                
                # Calcular cantidad del nutriente en la dieta usando valor BS
                cantidad_ingrediente_dieta = (porcentaje_en_formula / 100) * valor_bs
                cantidad_total_dieta += cantidad_ingrediente_dieta
                
                detalle_ingredientes.append({
                    'nombre': ingrediente_nombre,
                    'porcentaje_en_formula': porcentaje_en_formula,
                    'valor_tc': valor_tc,
                    'valor_bs': valor_bs,
                    'ms_ingrediente': ms_ingrediente,
                    'cantidad_en_dieta': round(cantidad_ingrediente_dieta, 4)
                })
            
            # Calcular aporte total según la unidad
            if nutriente_info['unidad'] == 'ppm':
                # ppm: multiplicar cantidad en dieta (ppm) × consumo (kg) = resultado en mg
                aporte_total_final = cantidad_total_dieta * consumo_animal
                unidad_final = 'mg'
                calculo_explicacion = f'{round(cantidad_total_dieta, 4)} ppm × {consumo_animal} kg = {round(aporte_total_final, 4)} mg'
            elif nutriente_info['unidad'] == '%':
                # %: multiplicar cantidad en dieta (%) × consumo (kg) ÷ 100 = resultado en kg
                aporte_total_final = (cantidad_total_dieta / 100) * consumo_animal
                unidad_final = 'kg'
                calculo_explicacion = f'{round(cantidad_total_dieta, 4)}% × {consumo_animal} kg ÷ 100 = {round(aporte_total_final, 4)} kg'
            elif nutriente_info['unidad'] == 'Kcal/kg':
                # Kcal/kg: multiplicar cantidad en dieta (Kcal/kg) × consumo (kg) = resultado en Kcal
                aporte_total_final = cantidad_total_dieta * consumo_animal
                unidad_final = 'Kcal'
                calculo_explicacion = f'{round(cantidad_total_dieta, 4)} Kcal/kg × {consumo_animal} kg = {round(aporte_total_final, 4)} Kcal'
            else:
                # Para otras unidades, mantener el cálculo original
                aporte_total_final = (cantidad_total_dieta / 100) * consumo_animal
                unidad_final = nutriente_info['unidad']
                calculo_explicacion = f'{round(cantidad_total_dieta, 4)} × {consumo_animal} kg = {round(aporte_total_final, 4)} {unidad_final}'
            
            resultados.append({
                'nutriente_id': nutriente_id,
                'nutriente_nombre': nutriente_info['nombre'],
                'unidad_original': nutriente_info['unidad'],
                'unidad_final': unidad_final,
                'cantidad_total_dieta': round(cantidad_total_dieta, 4),
                'aporte_total_final': round(aporte_total_final, 4),
                'detalle_ingredientes': detalle_ingredientes,
                'calculo_explicacion': calculo_explicacion
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'mezcla': mezcla,
            'consumo_animal': consumo_animal,
            'total_ingredientes': len(ingredientes_mezcla),
            'total_nutrientes': len(nutrientes_seleccionados),
            'resultados': resultados
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@calculadora_aportes_nueva_bp.route('/imprimir_aportes_mejorado')
@login_required
def imprimir_aportes_mejorado():
    """Página de impresión para aportes nutricionales mejorados"""
    try:
        # Obtener parámetros de la URL
        mezcla_id = request.args.get('mezcla_id')
        consumo_animal = float(request.args.get('consumo_animal', 0))
        nutrientes_seleccionados_str = request.args.get('nutrientes_seleccionados', '')
        
        if not mezcla_id or consumo_animal <= 0:
            return "Error: Parámetros inválidos", 400
        
        # Procesar nutrientes seleccionados
        nutrientes_seleccionados = []
        if nutrientes_seleccionados_str:
            try:
                nutrientes_seleccionados = [int(x.strip()) for x in nutrientes_seleccionados_str.split(',') if x.strip()]
            except ValueError:
                return "Error: Formato de nutrientes inválido", 400
        
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
            return "Error: Fórmula no encontrada", 404
        
        # Obtener ingredientes de la mezcla
        cursor.execute("""
            SELECT mi.ingrediente_id, mi.inclusion as porcentaje, i.nombre
            FROM mezcla_ingredientes mi
            JOIN ingredientes i ON mi.ingrediente_id = i.id
            WHERE mi.mezcla_id = %s
            ORDER BY mi.inclusion DESC
        """, (mezcla_id,))
        
        ingredientes_mezcla = cursor.fetchall()
        
        # Obtener nutrientes para mostrar en el reporte (solo los seleccionados si se especifican)
        if nutrientes_seleccionados:
            # Solo mostrar los nutrientes seleccionados
            placeholders = ','.join(['%s'] * len(nutrientes_seleccionados))
            cursor.execute(f"""
                SELECT DISTINCT n.id, n.nombre, n.unidad
                FROM nutrientes n
                WHERE n.usuario_id = %s AND n.id IN ({placeholders})
                ORDER BY n.nombre
            """, [session['user_id']] + nutrientes_seleccionados)
        else:
            # Mostrar todos los nutrientes disponibles (comportamiento original)
            cursor.execute("""
                SELECT DISTINCT n.id, n.nombre, n.unidad
                FROM nutrientes n
                JOIN ingredientes_nutrientes vn ON n.id = vn.nutriente_id
                JOIN mezcla_ingredientes mi ON vn.ingrediente_id = mi.ingrediente_id
                WHERE n.usuario_id = %s AND mi.mezcla_id = %s
                ORDER BY n.nombre
            """, (session['user_id'], mezcla_id))
        
        nutrientes_disponibles = cursor.fetchall()
        
        resultados = []
        
        # Calcular para cada nutriente disponible
        for nutriente in nutrientes_disponibles:
            cantidad_total_dieta = 0
            detalle_ingredientes = []
            
            for ingrediente in ingredientes_mezcla:
                # Obtener valor TC del nutriente para este ingrediente
                cursor.execute("""
                    SELECT valor
                    FROM ingredientes_nutrientes
                    WHERE ingrediente_id = %s AND nutriente_id = %s
                """, (ingrediente['ingrediente_id'], nutriente['id']))
                
                valor_resultado = cursor.fetchone()
                valor_tc = float(valor_resultado['valor']) if valor_resultado and valor_resultado['valor'] else 0
                
                # Obtener materia seca del ingrediente
                ms_ingrediente = float(ingrediente.get('ms', 100))
                
                # Calcular valor BS: valor_tc * (ms / 100)
                valor_bs = valor_tc * (ms_ingrediente / 100)
                
                if valor_bs > 0:  # Solo incluir si tiene valor BS
                    cantidad_ingrediente = (float(ingrediente['porcentaje']) / 100) * valor_bs
                    cantidad_total_dieta += cantidad_ingrediente
                    
                    detalle_ingredientes.append({
                        'nombre': ingrediente['nombre'],
                        'porcentaje': float(ingrediente['porcentaje']),
                        'valor_tc': valor_tc,
                        'valor_bs': valor_bs,
                        'ms_ingrediente': ms_ingrediente,
                        'cantidad_en_dieta': round(cantidad_ingrediente, 4)
                    })
            
            if cantidad_total_dieta > 0:  # Solo incluir nutrientes con valores
                # Calcular aporte final según unidad
                if nutriente['unidad'] == 'ppm':
                    aporte_final = cantidad_total_dieta * consumo_animal
                    unidad_final = 'mg'
                elif nutriente['unidad'] == '%':
                    aporte_final = (cantidad_total_dieta / 100) * consumo_animal
                    unidad_final = 'kg'
                elif nutriente['unidad'] == 'Kcal/kg':
                    aporte_final = cantidad_total_dieta * consumo_animal
                    unidad_final = 'Kcal'
                else:
                    aporte_final = cantidad_total_dieta * consumo_animal
                    unidad_final = nutriente['unidad']
                
                resultados.append({
                    'nutriente_nombre': nutriente['nombre'],
                    'unidad_original': nutriente['unidad'],
                    'unidad_final': unidad_final,
                    'cantidad_total_dieta': round(cantidad_total_dieta, 4),
                    'aporte_final': round(aporte_final, 4),
                    'detalle_ingredientes': detalle_ingredientes
                })
        
        cursor.close()
        conn.close()
        
        return render_template('operaciones/imprimir_aportes_mejorado.html',
                             mezcla=mezcla,
                             consumo_animal=consumo_animal,
                             total_ingredientes=len(ingredientes_mezcla),
                             total_nutrientes=len(resultados),
                             resultados=resultados,
                             fecha_actual=datetime.now().strftime('%d/%m/%Y %H:%M'))
        
    except Exception as e:
        return f"Error: {str(e)}", 500
