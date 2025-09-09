from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from app.db import get_db_connection
from functools import wraps

calculadora_ingredientes_bp = Blueprint('calculadora_ingredientes_bp', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth_bp.login'))
        return f(*args, **kwargs)
    return decorated_function

@calculadora_ingredientes_bp.route('/calculadora_ingredientes')
@login_required
def calculadora_ingredientes():
    """Página principal del estimador de necesidades de ingredientes"""
    return render_template('operaciones/calculadora_ingredientes.html')

@calculadora_ingredientes_bp.route('/api/obtener_formulas_ingredientes', methods=['GET'])
def obtener_formulas_ingredientes():
    """Obtener todas las fórmulas del usuario con sus ingredientes"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Obtener fórmulas del usuario
        cursor.execute("""
            SELECT m.id, m.nombre, m.fecha_creacion, m.costo_total,
                   COUNT(mi.id) as num_ingredientes
            FROM mezclas m
            LEFT JOIN mezcla_ingredientes mi ON m.id = mi.mezcla_id
            WHERE m.usuario_id = %s
            GROUP BY m.id, m.nombre, m.fecha_creacion, m.costo_total
            ORDER BY m.fecha_creacion DESC
        """, (session['user_id'],))
        
        formulas = cursor.fetchall()
        
        # Para cada fórmula, obtener sus ingredientes
        formulas_con_ingredientes = []
        for formula in formulas:
            cursor.execute("""
                SELECT mi.porcentaje, i.nombre as ingrediente_nombre, 
                       i.precio, i.ms, mi.ingrediente_id
                FROM mezcla_ingredientes mi
                JOIN ingredientes i ON mi.ingrediente_id = i.id
                WHERE mi.mezcla_id = %s
                ORDER BY mi.porcentaje DESC
            """, (formula['id'],))
            
            ingredientes = cursor.fetchall()
            
            formula_data = dict(formula)
            formula_data['ingredientes'] = ingredientes
            formulas_con_ingredientes.append(formula_data)
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'formulas': formulas_con_ingredientes
        })
        
    except Exception as e:
        print(f"Error obteniendo fórmulas: {e}")
        return jsonify({
            'success': False,
            'error': 'Error al cargar fórmulas'
        }), 500

@calculadora_ingredientes_bp.route('/api/calcular_necesidades', methods=['POST'])
def calcular_necesidades():
    """Calcular necesidades de ingredientes basado en fórmulas y cantidades"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        data = request.get_json()
        producciones = data.get('producciones', [])  # Lista de {formula_id, cantidad}
        
        if not producciones:
            return jsonify({
                'success': False,
                'error': 'No se han especificado producciones'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Diccionario para acumular necesidades por ingrediente
        necesidades_totales = {}
        resumen_producciones = []
        costo_total_produccion = 0
        
        for produccion in producciones:
            formula_id = produccion.get('formula_id')
            cantidad_producir = float(produccion.get('cantidad', 0))
            
            if not formula_id or cantidad_producir <= 0:
                continue
            
            # Verificar que la fórmula pertenece al usuario
            cursor.execute("""
                SELECT id, nombre, costo_total FROM mezclas 
                WHERE id = %s AND usuario_id = %s
            """, (formula_id, session['user_id']))
            
            formula = cursor.fetchone()
            if not formula:
                continue
            
            # Obtener ingredientes de la fórmula
            cursor.execute("""
                SELECT mi.porcentaje, i.nombre as ingrediente_nombre, 
                       i.precio, i.ms, mi.ingrediente_id, i.id
                FROM mezcla_ingredientes mi
                JOIN ingredientes i ON mi.ingrediente_id = i.id
                WHERE mi.mezcla_id = %s
            """, (formula_id,))
            
            ingredientes_formula = cursor.fetchall()
            
            # Calcular necesidades para esta producción
            necesidades_formula = []
            costo_formula = 0
            
            for ingrediente in ingredientes_formula:
                porcentaje = float(ingrediente['porcentaje'])
                precio_kg = float(ingrediente['precio'] or 0)
                nombre_ingrediente = ingrediente['ingrediente_nombre']
                ingrediente_id = ingrediente['id']
                
                # Calcular cantidad necesaria
                cantidad_necesaria = (cantidad_producir * porcentaje) / 100
                costo_ingrediente = cantidad_necesaria * precio_kg
                costo_formula += costo_ingrediente
                
                # Acumular en necesidades totales
                if ingrediente_id not in necesidades_totales:
                    necesidades_totales[ingrediente_id] = {
                        'nombre': nombre_ingrediente,
                        'cantidad_total': 0,
                        'costo_total': 0,
                        'precio_unitario': precio_kg,
                        'formulas_que_lo_usan': []
                    }
                
                necesidades_totales[ingrediente_id]['cantidad_total'] += cantidad_necesaria
                necesidades_totales[ingrediente_id]['costo_total'] += costo_ingrediente
                necesidades_totales[ingrediente_id]['formulas_que_lo_usan'].append({
                    'formula': formula['nombre'],
                    'cantidad': cantidad_necesaria,
                    'porcentaje': porcentaje
                })
                
                necesidades_formula.append({
                    'ingrediente': nombre_ingrediente,
                    'porcentaje': porcentaje,
                    'cantidad_necesaria': round(cantidad_necesaria, 3),
                    'precio_unitario': precio_kg,
                    'costo_total': round(costo_ingrediente, 2)
                })
            
            costo_total_produccion += costo_formula
            
            resumen_producciones.append({
                'formula': formula['nombre'],
                'cantidad_producir': cantidad_producir,
                'ingredientes': necesidades_formula,
                'costo_total': round(costo_formula, 2)
            })
        
        # Convertir necesidades totales a lista ordenada
        lista_necesidades = []
        for ingrediente_id, datos in necesidades_totales.items():
            lista_necesidades.append({
                'ingrediente_id': ingrediente_id,
                'nombre': datos['nombre'],
                'cantidad_total': round(datos['cantidad_total'], 3),
                'costo_total': round(datos['costo_total'], 2),
                'precio_unitario': datos['precio_unitario'],
                'formulas_que_lo_usan': datos['formulas_que_lo_usan']
            })
        
        # Ordenar por cantidad total descendente
        lista_necesidades.sort(key=lambda x: x['cantidad_total'], reverse=True)
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'necesidades_totales': lista_necesidades,
            'resumen_producciones': resumen_producciones,
            'costo_total_produccion': round(costo_total_produccion, 2),
            'estadisticas': {
                'total_ingredientes_diferentes': len(lista_necesidades),
                'total_producciones': len(resumen_producciones),
                'cantidad_total_producir': sum(p['cantidad_producir'] for p in resumen_producciones)
            }
        })
        
    except Exception as e:
        print(f"Error calculando necesidades: {e}")
        return jsonify({
            'success': False,
            'error': 'Error al calcular necesidades de ingredientes'
        }), 500

@calculadora_ingredientes_bp.route('/api/obtener_precios_ingredientes', methods=['GET'])
def obtener_precios_ingredientes():
    """Obtener precios actuales de todos los ingredientes del usuario"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, nombre, precio, ms, comentario
            FROM ingredientes
            WHERE usuario_id = %s
            ORDER BY nombre ASC
        """, (session['user_id'],))
        
        ingredientes = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'ingredientes': ingredientes
        })
        
    except Exception as e:
        print(f"Error obteniendo precios: {e}")
        return jsonify({
            'success': False,
            'error': 'Error al cargar precios de ingredientes'
        }), 500

@calculadora_ingredientes_bp.route('/api/actualizar_precio_ingrediente', methods=['POST'])
def actualizar_precio_ingrediente():
    """Actualizar precio de un ingrediente específico"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        data = request.get_json()
        ingrediente_id = data.get('ingrediente_id')
        nuevo_precio = float(data.get('nuevo_precio', 0))
        
        if not ingrediente_id:
            return jsonify({
                'success': False,
                'error': 'ID de ingrediente requerido'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar que el ingrediente pertenece al usuario y actualizarlo
        cursor.execute("""
            UPDATE ingredientes 
            SET precio = %s 
            WHERE id = %s AND usuario_id = %s
        """, (nuevo_precio, ingrediente_id, session['user_id']))
        
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Ingrediente no encontrado'
            }), 404
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'mensaje': 'Precio actualizado correctamente'
        })
        
    except ValueError:
        return jsonify({
            'success': False,
            'error': 'Precio debe ser un número válido'
        }), 400
    except Exception as e:
        print(f"Error actualizando precio: {e}")
        return jsonify({
            'success': False,
            'error': 'Error al actualizar precio'
        }), 500
