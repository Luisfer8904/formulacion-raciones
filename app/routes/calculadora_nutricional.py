from flask import Blueprint, request, jsonify, session, redirect, url_for
from functools import wraps

calculadora_nutricional_bp = Blueprint('calculadora_nutricional_bp', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth_bp.login'))
        return f(*args, **kwargs)
    return decorated_function

@calculadora_nutricional_bp.route('/api/calcular_nutriente_ms', methods=['POST'])
@login_required
def calcular_nutriente_ms():
    """API para cálculos nutricionales con materia seca"""
    try:
        data = request.get_json()
        tipo_nutriente = data.get('tipo_nutriente', 'proteina')
        porcentaje_nutriente = float(data.get('porcentaje_nutriente', 0))
        materia_seca = float(data.get('materia_seca', 88))
        cantidad = float(data.get('cantidad', 0))
        
        if porcentaje_nutriente < 0 or porcentaje_nutriente > 100:
            return jsonify({
                'success': False,
                'error': 'El porcentaje del nutriente debe estar entre 0 y 100'
            }), 400
            
        if materia_seca < 0 or materia_seca > 100:
            return jsonify({
                'success': False,
                'error': 'El porcentaje de materia seca debe estar entre 0 y 100'
            }), 400
            
        if cantidad <= 0:
            return jsonify({
                'success': False,
                'error': 'La cantidad debe ser mayor a 0'
            }), 400
        
        # Nombres de nutrientes
        nombres_nutrientes = {
            'proteina': 'Proteína Cruda',
            'grasa': 'Grasa Cruda',
            'fibra': 'Fibra Cruda',
            'cenizas': 'Cenizas',
            'carbohidratos': 'Carbohidratos',
            'energia': 'Energía Metabolizable'
        }
        
        nombre_nutriente = nombres_nutrientes.get(tipo_nutriente, 'Nutriente')
        unidad = 'Mcal' if tipo_nutriente == 'energia' else 'kg'
        
        # Cálculo: Cantidad * %MS * %Nutriente
        cantidad_ms = cantidad * (materia_seca / 100)
        
        if tipo_nutriente == 'energia':
            # Para energía no se divide por 100
            nutriente_total = cantidad_ms * porcentaje_nutriente
        else:
            nutriente_total = cantidad_ms * (porcentaje_nutriente / 100)
        
        return jsonify({
            'success': True,
            'tipo_nutriente': tipo_nutriente,
            'nombre_nutriente': nombre_nutriente,
            'cantidad_ms': round(cantidad_ms, 4),
            'nutriente_total': round(nutriente_total, 4),
            'unidad': unidad,
            'mensaje': f'{nombre_nutriente} total: {round(nutriente_total, 4)} {unidad}',
            'detalle': {
                'cantidad_original': cantidad,
                'materia_seca': materia_seca,
                'porcentaje_nutriente': porcentaje_nutriente,
                'calculo_paso_a_paso': [
                    f'1. Materia Seca: {cantidad} kg × {materia_seca}% = {round(cantidad_ms, 4)} kg',
                    f'2. {nombre_nutriente}: {round(cantidad_ms, 4)} kg × {porcentaje_nutriente}{"" if tipo_nutriente == "energia" else "%"} = {round(nutriente_total, 4)} {unidad}'
                ]
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
