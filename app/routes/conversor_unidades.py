from flask import Blueprint, request, jsonify, session, redirect, url_for
from functools import wraps

conversor_unidades_bp = Blueprint('conversor_unidades_bp', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth_bp.login'))
        return f(*args, **kwargs)
    return decorated_function

@conversor_unidades_bp.route('/api/convertir_unidades', methods=['POST'])
@login_required
def convertir_unidades():
    """API para conversión de unidades"""
    try:
        data = request.get_json()
        valor = float(data.get('valor', 0))
        origen = data.get('origen', '')
        destino = data.get('destino', '')
        
        # Tabla de conversiones
        conversiones = {
            'kg': {'g': 1000, 'lb': 2.20462, 'oz': 35.274, 'kg': 1},
            'g': {'kg': 0.001, 'lb': 0.00220462, 'oz': 0.035274, 'g': 1},
            'lb': {'kg': 0.453592, 'g': 453.592, 'oz': 16, 'lb': 1},
            'oz': {'kg': 0.0283495, 'g': 28.3495, 'lb': 0.0625, 'oz': 1}
        }
        
        if origen in conversiones and destino in conversiones[origen]:
            resultado = valor * conversiones[origen][destino]
            return jsonify({
                'success': True,
                'valor_original': valor,
                'unidad_origen': origen,
                'unidad_destino': destino,
                'resultado': round(resultado, 6),
                'mensaje': f'{valor} {origen} = {round(resultado, 6)} {destino}',
                'factor_conversion': conversiones[origen][destino]
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Conversión no soportada de {origen} a {destino}'
            }), 400
            
    except ValueError:
        return jsonify({
            'success': False,
            'error': 'Valor numérico inválido'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@conversor_unidades_bp.route('/api/unidades_disponibles', methods=['GET'])
@login_required
def unidades_disponibles():
    """API para obtener las unidades disponibles"""
    try:
        unidades = {
            'peso': [
                {'codigo': 'kg', 'nombre': 'Kilogramos', 'simbolo': 'kg'},
                {'codigo': 'g', 'nombre': 'Gramos', 'simbolo': 'g'},
                {'codigo': 'lb', 'nombre': 'Libras', 'simbolo': 'lb'},
                {'codigo': 'oz', 'nombre': 'Onzas', 'simbolo': 'oz'}
            ]
        }
        
        return jsonify({
            'success': True,
            'unidades': unidades
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
