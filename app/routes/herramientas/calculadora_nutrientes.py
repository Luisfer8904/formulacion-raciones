from flask import Blueprint, request, jsonify, session
from functools import wraps

calculadora_nutrientes_bp = Blueprint('calculadora_nutrientes_bp', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'No autorizado'}), 401
        return f(*args, **kwargs)
    return decorated_function

@calculadora_nutrientes_bp.route('/api/calcular_nutriente', methods=['POST'])
@login_required
def calcular_nutriente():
    """API para cálculo de nutrientes con materia seca"""
    try:
        data = request.get_json()
        porcentaje_nutriente = float(data.get('porcentaje_nutriente', 0))
        materia_seca = float(data.get('materia_seca', 100))
        cantidad = float(data.get('cantidad', 0))
        tipo_nutriente = data.get('tipo_nutriente', 'proteina')
        
        if cantidad <= 0:
            return jsonify({
                'success': False,
                'error': 'La cantidad debe ser mayor a 0'
            }), 400
        
        if materia_seca <= 0 or materia_seca > 100:
            return jsonify({
                'success': False,
                'error': 'La materia seca debe estar entre 0.1 y 100'
            }), 400
        
        # Cálculo: Cantidad * %MS * %Nutriente
        cantidad_ms = cantidad * (materia_seca / 100)
        
        if tipo_nutriente == 'energia':
            # Para energía no se divide por 100
            nutriente_total = cantidad_ms * porcentaje_nutriente
            unidad = 'Mcal'
        else:
            nutriente_total = cantidad_ms * (porcentaje_nutriente / 100)
            unidad = 'kg'
        
        nombres_nutrientes = {
            'proteina': 'Proteína Cruda',
            'grasa': 'Grasa Cruda',
            'fibra': 'Fibra Cruda',
            'cenizas': 'Cenizas',
            'carbohidratos': 'Carbohidratos',
            'energia': 'Energía Metabolizable'
        }
        
        nombre_nutriente = nombres_nutrientes.get(tipo_nutriente, 'Nutriente')
        
        return jsonify({
            'success': True,
            'resultado': round(nutriente_total, 4),
            'unidad': unidad,
            'nombre_nutriente': nombre_nutriente,
            'cantidad_ms': round(cantidad_ms, 4),
            'calculo': {
                'paso1': f'{cantidad} kg × {materia_seca}% = {round(cantidad_ms, 4)} kg MS',
                'paso2': f'{round(cantidad_ms, 4)} kg × {porcentaje_nutriente}{"%" if tipo_nutriente != "energia" else " Mcal/kg"} = {round(nutriente_total, 4)} {unidad}'
            }
        })
        
    except Exception as e:
        print(f"❌ Error en cálculo de nutriente: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500
