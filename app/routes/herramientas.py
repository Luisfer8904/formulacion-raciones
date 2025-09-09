from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from functools import wraps

herramientas_bp = Blueprint('herramientas_bp', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth_bp.login'))
        return f(*args, **kwargs)
    return decorated_function

@herramientas_bp.route('/herramientas')
@login_required
def herramientas():
    """Página principal de herramientas"""
    return render_template('operaciones/herramientas.html')

@herramientas_bp.route('/api/convertir_unidades', methods=['POST'])
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
