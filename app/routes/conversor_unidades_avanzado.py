from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from functools import wraps

conversor_avanzado_bp = Blueprint('conversor_avanzado_bp', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth_bp.login'))
        return f(*args, **kwargs)
    return decorated_function

# Definición completa de categorías y unidades como Google
CATEGORIAS_UNIDADES = {
    'longitud': {
        'nombre': 'Longitud',
        'icono': 'fas fa-ruler',
        'unidades': {
            'mm': {'nombre': 'Milímetro', 'factor': 0.001},
            'cm': {'nombre': 'Centímetro', 'factor': 0.01},
            'm': {'nombre': 'Metro', 'factor': 1.0},
            'km': {'nombre': 'Kilómetro', 'factor': 1000.0},
            'in': {'nombre': 'Pulgada', 'factor': 0.0254},
            'ft': {'nombre': 'Pie', 'factor': 0.3048},
            'yd': {'nombre': 'Yarda', 'factor': 0.9144},
            'mi': {'nombre': 'Milla', 'factor': 1609.34},
            'nmi': {'nombre': 'Milla náutica', 'factor': 1852.0}
        }
    },
    'masa': {
        'nombre': 'Masa',
        'icono': 'fas fa-weight',
        'unidades': {
            'mg': {'nombre': 'Miligramo', 'factor': 0.000001},
            'g': {'nombre': 'Gramo', 'factor': 0.001},
            'kg': {'nombre': 'Kilogramo', 'factor': 1.0},
            't': {'nombre': 'Tonelada', 'factor': 1000.0},
            'oz': {'nombre': 'Onza', 'factor': 0.0283495},
            'lb': {'nombre': 'Libra', 'factor': 0.453592},
            'st': {'nombre': 'Stone', 'factor': 6.35029}
        }
    },
    'volumen': {
        'nombre': 'Volumen',
        'icono': 'fas fa-flask',
        'unidades': {
            'ml': {'nombre': 'Mililitro', 'factor': 0.001},
            'l': {'nombre': 'Litro', 'factor': 1.0},
            'm3': {'nombre': 'Metro cúbico', 'factor': 1000.0},
            'tsp': {'nombre': 'Cucharadita', 'factor': 0.00492892},
            'tbsp': {'nombre': 'Cucharada', 'factor': 0.0147868},
            'fl_oz': {'nombre': 'Onza líquida', 'factor': 0.0295735},
            'cup': {'nombre': 'Taza', 'factor': 0.236588},
            'pt': {'nombre': 'Pinta', 'factor': 0.473176},
            'qt': {'nombre': 'Cuarto', 'factor': 0.946353},
            'gal': {'nombre': 'Galón', 'factor': 3.78541}
        }
    },
    'temperatura': {
        'nombre': 'Temperatura',
        'icono': 'fas fa-thermometer-half',
        'unidades': {
            'c': {'nombre': 'Celsius', 'factor': 1.0},
            'f': {'nombre': 'Fahrenheit', 'factor': 1.0},
            'k': {'nombre': 'Kelvin', 'factor': 1.0},
            'r': {'nombre': 'Rankine', 'factor': 1.0}
        }
    },
    'tiempo': {
        'nombre': 'Tiempo',
        'icono': 'fas fa-clock',
        'unidades': {
            'ms': {'nombre': 'Milisegundo', 'factor': 0.001},
            's': {'nombre': 'Segundo', 'factor': 1.0},
            'min': {'nombre': 'Minuto', 'factor': 60.0},
            'h': {'nombre': 'Hora', 'factor': 3600.0},
            'd': {'nombre': 'Día', 'factor': 86400.0},
            'w': {'nombre': 'Semana', 'factor': 604800.0},
            'mo': {'nombre': 'Mes', 'factor': 2629746.0},
            'y': {'nombre': 'Año', 'factor': 31556952.0}
        }
    },
    'velocidad': {
        'nombre': 'Velocidad',
        'icono': 'fas fa-tachometer-alt',
        'unidades': {
            'mps': {'nombre': 'Metro/segundo', 'factor': 1.0},
            'kmh': {'nombre': 'Kilómetro/hora', 'factor': 0.277778},
            'mph': {'nombre': 'Milla/hora', 'factor': 0.44704},
            'kn': {'nombre': 'Nudo', 'factor': 0.514444},
            'fps': {'nombre': 'Pie/segundo', 'factor': 0.3048}
        }
    },
    'presion': {
        'nombre': 'Presión',
        'icono': 'fas fa-compress-arrows-alt',
        'unidades': {
            'pa': {'nombre': 'Pascal', 'factor': 1.0},
            'kpa': {'nombre': 'Kilopascal', 'factor': 1000.0},
            'mpa': {'nombre': 'Megapascal', 'factor': 1000000.0},
            'bar': {'nombre': 'Bar', 'factor': 100000.0},
            'atm': {'nombre': 'Atmósfera', 'factor': 101325.0},
            'psi': {'nombre': 'PSI', 'factor': 6894.76},
            'mmhg': {'nombre': 'mmHg', 'factor': 133.322}
        }
    },
    'energia': {
        'nombre': 'Energía',
        'icono': 'fas fa-bolt',
        'unidades': {
            'j': {'nombre': 'Joule', 'factor': 1.0},
            'kj': {'nombre': 'Kilojoule', 'factor': 1000.0},
            'cal': {'nombre': 'Caloría', 'factor': 4.184},
            'kcal': {'nombre': 'Kilocaloría', 'factor': 4184.0},
            'wh': {'nombre': 'Vatio-hora', 'factor': 3600.0},
            'kwh': {'nombre': 'Kilovatio-hora', 'factor': 3600000.0},
            'btu': {'nombre': 'BTU', 'factor': 1055.06}
        }
    },
    'frecuencia': {
        'nombre': 'Frecuencia',
        'icono': 'fas fa-wave-square',
        'unidades': {
            'hz': {'nombre': 'Hertz', 'factor': 1.0},
            'khz': {'nombre': 'Kilohertz', 'factor': 1000.0},
            'mhz': {'nombre': 'Megahertz', 'factor': 1000000.0},
            'ghz': {'nombre': 'Gigahertz', 'factor': 1000000000.0}
        }
    },
    'area': {
        'nombre': 'Área',
        'icono': 'fas fa-vector-square',
        'unidades': {
            'mm2': {'nombre': 'Milímetro²', 'factor': 0.000001},
            'cm2': {'nombre': 'Centímetro²', 'factor': 0.0001},
            'm2': {'nombre': 'Metro²', 'factor': 1.0},
            'km2': {'nombre': 'Kilómetro²', 'factor': 1000000.0},
            'in2': {'nombre': 'Pulgada²', 'factor': 0.00064516},
            'ft2': {'nombre': 'Pie²', 'factor': 0.092903},
            'yd2': {'nombre': 'Yarda²', 'factor': 0.836127},
            'ac': {'nombre': 'Acre', 'factor': 4046.86},
            'ha': {'nombre': 'Hectárea', 'factor': 10000.0}
        }
    },
    'angulo': {
        'nombre': 'Ángulo plano',
        'icono': 'fas fa-drafting-compass',
        'unidades': {
            'deg': {'nombre': 'Grado', 'factor': 1.0},
            'rad': {'nombre': 'Radián', 'factor': 57.2958},
            'grad': {'nombre': 'Gradián', 'factor': 0.9},
            'turn': {'nombre': 'Vuelta', 'factor': 360.0}
        }
    },
    'datos': {
        'nombre': 'Tamaño de datos',
        'icono': 'fas fa-hdd',
        'unidades': {
            'b': {'nombre': 'Byte', 'factor': 1.0},
            'kb': {'nombre': 'Kilobyte', 'factor': 1024.0},
            'mb': {'nombre': 'Megabyte', 'factor': 1048576.0},
            'gb': {'nombre': 'Gigabyte', 'factor': 1073741824.0},
            'tb': {'nombre': 'Terabyte', 'factor': 1099511627776.0},
            'pb': {'nombre': 'Petabyte', 'factor': 1125899906842624.0}
        }
    },
    'transmision': {
        'nombre': 'Tasa de transmisión de datos',
        'icono': 'fas fa-wifi',
        'unidades': {
            'bps': {'nombre': 'Bit/segundo', 'factor': 1.0},
            'kbps': {'nombre': 'Kilobit/segundo', 'factor': 1000.0},
            'mbps': {'nombre': 'Megabit/segundo', 'factor': 1000000.0},
            'gbps': {'nombre': 'Gigabit/segundo', 'factor': 1000000000.0}
        }
    }
}

def convertir_temperatura(valor, unidad_origen, unidad_destino):
    """Conversión especial para temperatura"""
    # Convertir a Celsius primero
    if unidad_origen == 'f':
        celsius = (valor - 32) * 5/9
    elif unidad_origen == 'k':
        celsius = valor - 273.15
    elif unidad_origen == 'r':
        celsius = (valor - 491.67) * 5/9
    else:  # Celsius
        celsius = valor
    
    # Convertir de Celsius a la unidad destino
    if unidad_destino == 'f':
        return celsius * 9/5 + 32
    elif unidad_destino == 'k':
        return celsius + 273.15
    elif unidad_destino == 'r':
        return celsius * 9/5 + 491.67
    else:  # Celsius
        return celsius

def convertir_angulo(valor, unidad_origen, unidad_destino):
    """Conversión especial para ángulos"""
    # Convertir a grados primero
    if unidad_origen == 'rad':
        grados = valor * 180 / 3.14159265359
    elif unidad_origen == 'grad':
        grados = valor * 0.9
    elif unidad_origen == 'turn':
        grados = valor * 360
    else:  # grados
        grados = valor
    
    # Convertir de grados a la unidad destino
    if unidad_destino == 'rad':
        return grados * 3.14159265359 / 180
    elif unidad_destino == 'grad':
        return grados / 0.9
    elif unidad_destino == 'turn':
        return grados / 360
    else:  # grados
        return grados

@conversor_avanzado_bp.route('/conversor_avanzado')
@login_required
def conversor_avanzado():
    """Página del conversor de unidades avanzado estilo Google"""
    return render_template('operaciones/conversor_avanzado.html', 
                         categorias=CATEGORIAS_UNIDADES)

@conversor_avanzado_bp.route('/api/convertir_avanzado', methods=['POST'])
def convertir_avanzado():
    """API para conversión avanzada de unidades"""
    try:
        data = request.get_json()
        valor = float(data.get('valor', 0))
        categoria = data.get('categoria')
        unidad_origen = data.get('unidad_origen')
        unidad_destino = data.get('unidad_destino')
        
        if not all([categoria, unidad_origen, unidad_destino]):
            return jsonify({
                'success': False,
                'error': 'Parámetros incompletos'
            }), 400
        
        if categoria not in CATEGORIAS_UNIDADES:
            return jsonify({
                'success': False,
                'error': 'Categoría no válida'
            }), 400
        
        categoria_data = CATEGORIAS_UNIDADES[categoria]
        
        if unidad_origen not in categoria_data['unidades'] or unidad_destino not in categoria_data['unidades']:
            return jsonify({
                'success': False,
                'error': 'Unidades no válidas para esta categoría'
            }), 400
        
        # Conversiones especiales
        if categoria == 'temperatura':
            resultado = convertir_temperatura(valor, unidad_origen, unidad_destino)
        elif categoria == 'angulo':
            resultado = convertir_angulo(valor, unidad_origen, unidad_destino)
        else:
            # Conversión estándar usando factores
            factor_origen = categoria_data['unidades'][unidad_origen]['factor']
            factor_destino = categoria_data['unidades'][unidad_destino]['factor']
            
            # Convertir a unidad base y luego a unidad destino
            valor_base = valor * factor_origen
            resultado = valor_base / factor_destino
        
        # Formatear resultado
        if abs(resultado) >= 1000000:
            resultado_formateado = f"{resultado:.2e}"
        elif abs(resultado) >= 1000:
            resultado_formateado = f"{resultado:,.2f}"
        elif abs(resultado) >= 1:
            resultado_formateado = f"{resultado:.4f}".rstrip('0').rstrip('.')
        else:
            resultado_formateado = f"{resultado:.6f}".rstrip('0').rstrip('.')
        
        nombre_origen = categoria_data['unidades'][unidad_origen]['nombre']
        nombre_destino = categoria_data['unidades'][unidad_destino]['nombre']
        
        return jsonify({
            'success': True,
            'resultado': resultado,
            'resultado_formateado': resultado_formateado,
            'mensaje': f"{valor} {nombre_origen} = {resultado_formateado} {nombre_destino}",
            'formula': f"1 {nombre_origen} = {factor_origen/factor_destino if categoria not in ['temperatura', 'angulo'] else 'Fórmula especial'} {nombre_destino}" if categoria not in ['temperatura', 'angulo'] else None
        })
        
    except ValueError:
        return jsonify({
            'success': False,
            'error': 'Valor numérico no válido'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error en la conversión: {str(e)}'
        }), 500

@conversor_avanzado_bp.route('/api/obtener_unidades/<categoria>')
def obtener_unidades(categoria):
    """Obtener unidades disponibles para una categoría"""
    if categoria not in CATEGORIAS_UNIDADES:
        return jsonify({
            'success': False,
            'error': 'Categoría no encontrada'
        }), 404
    
    return jsonify({
        'success': True,
        'unidades': CATEGORIAS_UNIDADES[categoria]['unidades'],
        'nombre_categoria': CATEGORIAS_UNIDADES[categoria]['nombre']
    })
