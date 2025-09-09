from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from app.db import get_db_connection
from functools import wraps

reporte_comparativo_bp = Blueprint('reporte_comparativo_bp', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth_bp.login'))
        return f(*args, **kwargs)
    return decorated_function

@reporte_comparativo_bp.route('/reporte_comparativo')
@login_required
def reporte_comparativo():
    """Página principal del reporte comparativo de fórmulas"""
    return render_template('operaciones/reporte_comparativo.html')

@reporte_comparativo_bp.route('/api/obtener_formulas_usuario', methods=['GET'])
def obtener_formulas_usuario():
    """Obtener todas las fórmulas/mezclas del usuario para comparación"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Obtener mezclas del usuario con información básica
        cursor.execute("""
            SELECT m.id, m.nombre, m.fecha_creacion, m.costo_total,
                   COUNT(mi.id) as num_ingredientes
            FROM mezclas m
            LEFT JOIN mezcla_ingredientes mi ON m.id = mi.mezcla_id
            WHERE m.usuario_id = %s
            GROUP BY m.id, m.nombre, m.fecha_creacion, m.costo_total
            ORDER BY m.fecha_creacion DESC
        """, (session['user_id'],))
        
        formulas_raw = cursor.fetchall()
        
        # Convertir a lista de diccionarios para asegurar compatibilidad
        formulas = []
        for formula in formulas_raw:
            formulas.append({
                'id': formula['id'],
                'nombre': formula['nombre'],
                'fecha_creacion': formula['fecha_creacion'].isoformat() if formula['fecha_creacion'] else None,
                'costo_total': float(formula['costo_total']) if formula['costo_total'] else 0.0,
                'num_ingredientes': int(formula['num_ingredientes']) if formula['num_ingredientes'] else 0
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'formulas': formulas
        })
        
    except Exception as e:
        print(f"Error obteniendo fórmulas: {e}")
        return jsonify({
            'success': False,
            'error': 'Error al cargar fórmulas'
        }), 500

@reporte_comparativo_bp.route('/api/obtener_nutrientes_disponibles', methods=['GET'])
def obtener_nutrientes_disponibles():
    """Obtener todos los nutrientes disponibles del usuario"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Obtener nutrientes del usuario
        cursor.execute("""
            SELECT id, nombre, unidad, tipo
            FROM nutrientes
            WHERE usuario_id = %s
            ORDER BY nombre ASC
        """, (session['user_id'],))
        
        nutrientes = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'nutrientes': nutrientes
        })
        
    except Exception as e:
        print(f"Error obteniendo nutrientes: {e}")
        return jsonify({
            'success': False,
            'error': 'Error al cargar nutrientes'
        }), 500

@reporte_comparativo_bp.route('/api/obtener_composicion_formula/<int:formula_id>', methods=['GET'])
def obtener_composicion_formula(formula_id):
    """Obtener la composición nutricional de una fórmula específica"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que la fórmula pertenece al usuario
        cursor.execute("""
            SELECT id, nombre FROM mezclas 
            WHERE id = %s AND usuario_id = %s
        """, (formula_id, session['user_id']))
        
        formula = cursor.fetchone()
        if not formula:
            return jsonify({
                'success': False,
                'error': 'Fórmula no encontrada'
            }), 404
        
        # Obtener ingredientes de la fórmula
        cursor.execute("""
            SELECT mi.porcentaje, i.nombre as ingrediente_nombre, i.ms,
                   mi.ingrediente_id
            FROM mezcla_ingredientes mi
            JOIN ingredientes i ON mi.ingrediente_id = i.id
            WHERE mi.mezcla_id = %s
        """, (formula_id,))
        
        ingredientes_formula = cursor.fetchall()
        
        # Obtener todos los nutrientes del usuario
        cursor.execute("""
            SELECT id, nombre, unidad
            FROM nutrientes
            WHERE usuario_id = %s
            ORDER BY nombre ASC
        """, (session['user_id'],))
        
        nutrientes = cursor.fetchall()
        
        # Calcular composición nutricional
        composicion_nutricional = {}
        
        for nutriente in nutrientes:
            nutriente_id = nutriente['id']
            nutriente_nombre = nutriente['nombre']
            total_nutriente = 0.0
            
            for ingrediente in ingredientes_formula:
                ingrediente_id = ingrediente['ingrediente_id']
                porcentaje_ingrediente = float(ingrediente['porcentaje'])
                ms_ingrediente = float(ingrediente['ms'])
                
                # Obtener valor del nutriente para este ingrediente
                cursor.execute("""
                    SELECT valor
                    FROM ingredientes_nutrientes
                    WHERE ingrediente_id = %s AND nutriente_id = %s
                """, (ingrediente_id, nutriente_id))
                
                valor_nutriente = cursor.fetchone()
                if valor_nutriente:
                    valor = float(valor_nutriente['valor'])
                    # Calcular aporte: (porcentaje_ingrediente/100) * (ms/100) * valor
                    aporte = (porcentaje_ingrediente / 100) * (ms_ingrediente / 100) * valor
                    total_nutriente += aporte
            
            composicion_nutricional[nutriente_nombre] = {
                'valor': round(total_nutriente, 4),
                'unidad': nutriente['unidad']
            }
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'formula': formula,
            'ingredientes': ingredientes_formula,
            'composicion_nutricional': composicion_nutricional
        })
        
    except Exception as e:
        print(f"Error obteniendo composición: {e}")
        return jsonify({
            'success': False,
            'error': 'Error al calcular composición nutricional'
        }), 500

@reporte_comparativo_bp.route('/api/comparar_formulas', methods=['POST'])
def comparar_formulas():
    """Comparar dos fórmulas en nutrientes específicos"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        data = request.get_json()
        formula1_id = data.get('formula1_id')
        formula2_id = data.get('formula2_id')
        nutrientes_seleccionados = data.get('nutrientes_seleccionados', [])
        
        if not formula1_id or not formula2_id:
            return jsonify({
                'success': False,
                'error': 'Debe seleccionar dos fórmulas'
            }), 400
        
        if not nutrientes_seleccionados:
            return jsonify({
                'success': False,
                'error': 'Debe seleccionar al menos un nutriente'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Obtener composición de ambas fórmulas
        composiciones = {}
        
        for formula_id in [formula1_id, formula2_id]:
            # Verificar que la fórmula pertenece al usuario
            cursor.execute("""
                SELECT id, nombre FROM mezclas 
                WHERE id = %s AND usuario_id = %s
            """, (formula_id, session['user_id']))
            
            formula = cursor.fetchone()
            if not formula:
                return jsonify({
                    'success': False,
                    'error': f'Fórmula {formula_id} no encontrada'
                }), 404
            
            # Obtener ingredientes de la fórmula
            cursor.execute("""
                SELECT mi.porcentaje, i.nombre as ingrediente_nombre, i.ms,
                       mi.ingrediente_id
                FROM mezcla_ingredientes mi
                JOIN ingredientes i ON mi.ingrediente_id = i.id
                WHERE mi.mezcla_id = %s
            """, (formula_id,))
            
            ingredientes_formula = cursor.fetchall()
            
            # Calcular composición para nutrientes seleccionados
            composicion = {'formula': formula, 'nutrientes': {}}
            
            for nutriente_nombre in nutrientes_seleccionados:
                # Obtener ID del nutriente
                cursor.execute("""
                    SELECT id, unidad FROM nutrientes
                    WHERE nombre = %s AND usuario_id = %s
                """, (nutriente_nombre, session['user_id']))
                
                nutriente = cursor.fetchone()
                if not nutriente:
                    continue
                
                nutriente_id = nutriente['id']
                total_nutriente = 0.0
                
                for ingrediente in ingredientes_formula:
                    ingrediente_id = ingrediente['ingrediente_id']
                    porcentaje_ingrediente = float(ingrediente['porcentaje'])
                    ms_ingrediente = float(ingrediente['ms'])
                    
                    # Obtener valor del nutriente para este ingrediente
                    cursor.execute("""
                        SELECT valor
                        FROM ingredientes_nutrientes
                        WHERE ingrediente_id = %s AND nutriente_id = %s
                    """, (ingrediente_id, nutriente_id))
                    
                    valor_nutriente = cursor.fetchone()
                    if valor_nutriente:
                        valor = float(valor_nutriente['valor'])
                        # Calcular aporte: (porcentaje_ingrediente/100) * (ms/100) * valor
                        aporte = (porcentaje_ingrediente / 100) * (ms_ingrediente / 100) * valor
                        total_nutriente += aporte
                
                composicion['nutrientes'][nutriente_nombre] = {
                    'valor': round(total_nutriente, 4),
                    'unidad': nutriente['unidad']
                }
            
            composiciones[f'formula_{formula_id}'] = composicion
        
        # Calcular diferencias y porcentajes
        comparacion = {
            'formula1': composiciones[f'formula_{formula1_id}'],
            'formula2': composiciones[f'formula_{formula2_id}'],
            'diferencias': {},
            'resumen': {
                'nutrientes_comparados': len(nutrientes_seleccionados),
                'formula1_mejor': 0,
                'formula2_mejor': 0,
                'iguales': 0
            }
        }
        
        for nutriente in nutrientes_seleccionados:
            if nutriente in comparacion['formula1']['nutrientes'] and nutriente in comparacion['formula2']['nutrientes']:
                valor1 = comparacion['formula1']['nutrientes'][nutriente]['valor']
                valor2 = comparacion['formula2']['nutrientes'][nutriente]['valor']
                diferencia = valor2 - valor1
                porcentaje_diferencia = ((valor2 - valor1) / valor1 * 100) if valor1 != 0 else 0
                
                comparacion['diferencias'][nutriente] = {
                    'diferencia_absoluta': round(diferencia, 4),
                    'diferencia_porcentual': round(porcentaje_diferencia, 2),
                    'unidad': comparacion['formula1']['nutrientes'][nutriente]['unidad']
                }
                
                # Actualizar resumen
                if abs(diferencia) < 0.001:  # Prácticamente iguales
                    comparacion['resumen']['iguales'] += 1
                elif diferencia > 0:
                    comparacion['resumen']['formula2_mejor'] += 1
                else:
                    comparacion['resumen']['formula1_mejor'] += 1
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'comparacion': comparacion
        })
        
    except Exception as e:
        print(f"Error comparando fórmulas: {e}")
        return jsonify({
            'success': False,
            'error': 'Error al comparar fórmulas'
        }), 500
