from flask import Blueprint, request, jsonify, session
from functools import wraps
from app.db import get_db_connection

gestion_limites_bp = Blueprint('gestion_limites_bp', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'No autorizado'}), 401
        return f(*args, **kwargs)
    return decorated_function

@gestion_limites_bp.route('/api/ingredientes_con_limites', methods=['GET'])
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

@gestion_limites_bp.route('/api/actualizar_limites_ingrediente', methods=['POST'])
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
        
        # Verificar si las columnas existen antes de actualizar
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'ingredientes'
            AND COLUMN_NAME IN ('limite_min', 'limite_max')
        """)
        
        columnas_limites = cursor.fetchall()
        
        if len(columnas_limites) == 2:
            # Actualizar límites
            cursor.execute("""
                UPDATE ingredientes 
                SET limite_min = %s, limite_max = %s 
                WHERE id = %s AND usuario_id = %s
            """, (limite_min, limite_max, ingrediente_id, session['user_id']))
            
            conn.commit()
            mensaje = 'Límites actualizados correctamente'
        else:
            mensaje = 'Las columnas de límites no existen. Ejecute la migración primero.'
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'mensaje': mensaje
        })
        
    except Exception as e:
        print(f"❌ Error al actualizar límites: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@gestion_limites_bp.route('/api/verificar_migracion_limites', methods=['GET'])
@login_required
def verificar_migracion_limites():
    """API para verificar si la migración de límites se ha ejecutado"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar si las columnas de límites existen
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'ingredientes'
            AND COLUMN_NAME IN ('limite_min', 'limite_max')
            ORDER BY COLUMN_NAME
        """)
        
        columnas = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'migracion_ejecutada': len(columnas) == 2,
            'columnas_encontradas': len(columnas),
            'detalles': columnas
        })
        
    except Exception as e:
        print(f"❌ Error al verificar migración: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500
