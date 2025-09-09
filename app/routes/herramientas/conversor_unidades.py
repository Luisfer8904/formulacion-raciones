from flask import Blueprint, request, jsonify, session
from functools import wraps

conversor_unidades_bp = Blueprint('conversor_unidades_bp', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'No autorizado'}), 401
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
