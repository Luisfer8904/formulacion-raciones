from flask import Blueprint, request, jsonify, session, redirect, url_for
from functools import wraps

herramientas_basicas_bp = Blueprint('herramientas_basicas_bp', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth_bp.login'))
        return f(*args, **kwargs)
    return decorated_function

@herramientas_basicas_bp.route('/api/convertir_unidades', methods=['POST'])
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
                'resultado': round(resultado, 6),
                'mensaje': f'{valor} {origen} = {round(resultado, 6)} {destino}'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Conversión no soportada'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@herramientas_basicas_bp.route('/api/calcular_nutriente', methods=['POST'])
@login_required
def calcular_nutriente():
    """API para cálculos nutricionales"""
    try:
        data = request.get_json()
        porcentaje = float(data.get('porcentaje', 0))
        cantidad = float(data.get('cantidad', 0))
        nutriente = data.get('nutriente', 'Nutriente')
        
        if porcentaje < 0 or porcentaje > 100:
            return jsonify({
                'success': False,
                'error': 'El porcentaje debe estar entre 0 y 100'
            }), 400
            
        if cantidad <= 0:
            return jsonify({
                'success': False,
                'error': 'La cantidad debe ser mayor a 0'
            }), 400
        
        total_nutriente = (porcentaje / 100) * cantidad
        
        return jsonify({
            'success': True,
            'resultado': round(total_nutriente, 4),
            'mensaje': f'{nutriente} total: {round(total_nutriente, 4)} kg',
            'detalle': f'En {cantidad} kg de alimento con {porcentaje}% de {nutriente.lower()}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

