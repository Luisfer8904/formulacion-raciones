from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
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

@herramientas_bp.route('/api/calcular_nutriente', methods=['POST'])
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

@herramientas_bp.route('/api/analizar_costos', methods=['POST'])
@login_required
def analizar_costos():
    """API para análisis de costos"""
    try:
        data = request.get_json()
        ingredientes = data.get('ingredientes', [])
        
        if not ingredientes:
            return jsonify({
                'success': False,
                'error': 'No se proporcionaron ingredientes'
            }), 400
        
        costo_total = 0
        analisis = []
        
        for ing in ingredientes:
            nombre = ing.get('nombre', '')
            cantidad = float(ing.get('cantidad', 0))
            precio_kg = float(ing.get('precio_kg', 0))
            
            costo_ingrediente = cantidad * precio_kg
            costo_total += costo_ingrediente
            
            analisis.append({
                'nombre': nombre,
                'cantidad': cantidad,
                'precio_kg': precio_kg,
                'costo_total': round(costo_ingrediente, 2),
                'porcentaje': 0  # Se calculará después
            })
        
        # Calcular porcentajes
        for item in analisis:
            if costo_total > 0:
                item['porcentaje'] = round((item['costo_total'] / costo_total) * 100, 2)
        
        return jsonify({
            'success': True,
            'costo_total': round(costo_total, 2),
            'analisis': analisis,
            'ingrediente_mas_caro': max(analisis, key=lambda x: x['costo_total']) if analisis else None
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@herramientas_bp.route('/api/validar_formula', methods=['POST'])
@login_required
def validar_formula():
    """API para validación de fórmulas"""
    try:
        data = request.get_json()
        ingredientes = data.get('ingredientes', [])
        requerimientos = data.get('requerimientos', {})
        
        if not ingredientes:
            return jsonify({
                'success': False,
                'error': 'No se proporcionaron ingredientes'
            }), 400
        
        # Validaciones básicas
        validaciones = []
        errores = []
        advertencias = []
        
        # Verificar que la suma de porcentajes sea 100%
        total_porcentaje = sum(float(ing.get('porcentaje', 0)) for ing in ingredientes)
        
        if abs(total_porcentaje - 100) > 0.1:
            errores.append(f'La suma de porcentajes es {total_porcentaje}%, debe ser 100%')
        else:
            validaciones.append('✓ Suma de porcentajes correcta (100%)')
        
        # Verificar ingredientes con porcentaje 0
        ingredientes_cero = [ing['nombre'] for ing in ingredientes if float(ing.get('porcentaje', 0)) == 0]
        if ingredientes_cero:
            advertencias.append(f'Ingredientes con 0%: {", ".join(ingredientes_cero)}')
        
        # Verificar ingredientes con porcentaje muy alto
        ingredientes_altos = [ing['nombre'] for ing in ingredientes if float(ing.get('porcentaje', 0)) > 50]
        if ingredientes_altos:
            advertencias.append(f'Ingredientes con >50%: {", ".join(ingredientes_altos)}')
        
        # Calcular estado general
        if errores:
            estado = 'error'
        elif advertencias:
            estado = 'advertencia'
        else:
            estado = 'valida'
        
        return jsonify({
            'success': True,
            'estado': estado,
            'validaciones': validaciones,
            'errores': errores,
            'advertencias': advertencias,
            'total_ingredientes': len(ingredientes),
            'total_porcentaje': round(total_porcentaje, 2)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
