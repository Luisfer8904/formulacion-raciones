from flask import Blueprint, request, jsonify, session
from functools import wraps
from typing import Any, Dict

conversor_unidades_avanzado_bp = Blueprint('conversor_unidades_avanzado_bp', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'No autorizado'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Definir todas las categorías y unidades con sus factores de conversión
UNIDADES_CONVERSION = {
    'longitud': {
        'nombre': 'Longitud',
        'unidades': {
            'metro': {'nombre': 'Metro', 'simbolo': 'm', 'factor': 1.0},
            'kilometro': {'nombre': 'Kilómetro', 'simbolo': 'km', 'factor': 1000.0},
            'centimetro': {'nombre': 'Centímetro', 'simbolo': 'cm', 'factor': 0.01},
            'milimetro': {'nombre': 'Milímetro', 'simbolo': 'mm', 'factor': 0.001},
            'micrometro': {'nombre': 'Micrómetro', 'simbolo': 'μm', 'factor': 0.000001},
            'nanometro': {'nombre': 'Nanómetro', 'simbolo': 'nm', 'factor': 0.000000001},
            'milla': {'nombre': 'Milla', 'simbolo': 'mi', 'factor': 1609.344},
            'yarda': {'nombre': 'Yarda', 'simbolo': 'yd', 'factor': 0.9144},
            'pie': {'nombre': 'Pie', 'simbolo': 'ft', 'factor': 0.3048},
            'pulgada': {'nombre': 'Pulgada', 'simbolo': 'in', 'factor': 0.0254},
            'milla_nautica': {'nombre': 'Milla náutica', 'simbolo': 'nmi', 'factor': 1852.0}
        }
    },
    'masa': {
        'nombre': 'Masa',
        'unidades': {
            'kilogramo': {'nombre': 'Kilogramo', 'simbolo': 'kg', 'factor': 1.0},
            'gramo': {'nombre': 'Gramo', 'simbolo': 'g', 'factor': 0.001},
            'miligramo': {'nombre': 'Miligramo', 'simbolo': 'mg', 'factor': 0.000001},
            'tonelada': {'nombre': 'Tonelada', 'simbolo': 't', 'factor': 1000.0},
            'libra': {'nombre': 'Libra', 'simbolo': 'lb', 'factor': 0.453592},
            'onza': {'nombre': 'Onza', 'simbolo': 'oz', 'factor': 0.0283495},
            'quintal': {'nombre': 'Quintal', 'simbolo': 'q', 'factor': 100.0},
            'arroba': {'nombre': 'Arroba', 'simbolo': '@', 'factor': 11.502}
        }
    },
    'volumen': {
        'nombre': 'Volumen',
        'unidades': {
            'litro': {'nombre': 'Litro', 'simbolo': 'L', 'factor': 1.0},
            'mililitro': {'nombre': 'Mililitro', 'simbolo': 'mL', 'factor': 0.001},
            'metro_cubico': {'nombre': 'Metro cúbico', 'simbolo': 'm³', 'factor': 1000.0},
            'centimetro_cubico': {'nombre': 'Centímetro cúbico', 'simbolo': 'cm³', 'factor': 0.001},
            'galon_us': {'nombre': 'Galón (US)', 'simbolo': 'gal', 'factor': 3.78541},
            'galon_imperial': {'nombre': 'Galón (Imperial)', 'simbolo': 'gal imp', 'factor': 4.54609},
            'cuarto': {'nombre': 'Cuarto', 'simbolo': 'qt', 'factor': 0.946353},
            'pinta': {'nombre': 'Pinta', 'simbolo': 'pt', 'factor': 0.473176},
            'onza_fluida': {'nombre': 'Onza fluida', 'simbolo': 'fl oz', 'factor': 0.0295735},
            'barril': {'nombre': 'Barril', 'simbolo': 'bbl', 'factor': 158.987}
        }
    },
    'temperatura': {
        'nombre': 'Temperatura',
        'unidades': {
            'celsius': {'nombre': 'Celsius', 'simbolo': '°C', 'factor': 1.0},
            'fahrenheit': {'nombre': 'Fahrenheit', 'simbolo': '°F', 'factor': 1.0},
            'kelvin': {'nombre': 'Kelvin', 'simbolo': 'K', 'factor': 1.0},
            'rankine': {'nombre': 'Rankine', 'simbolo': '°R', 'factor': 1.0}
        }
    },
    'energia': {
        'nombre': 'Energía',
        'unidades': {
            'joule': {'nombre': 'Joule', 'simbolo': 'J', 'factor': 1.0},
            'kilojoule': {'nombre': 'Kilojoule', 'simbolo': 'kJ', 'factor': 1000.0},
            'caloria': {'nombre': 'Caloría', 'simbolo': 'cal', 'factor': 4.184},
            'kilocaloria': {'nombre': 'Kilocaloría', 'simbolo': 'kcal', 'factor': 4184.0},
            'megacaloria': {'nombre': 'Megacaloría', 'simbolo': 'Mcal', 'factor': 4184000.0},
            'watt_hora': {'nombre': 'Watt-hora', 'simbolo': 'Wh', 'factor': 3600.0},
            'kilowatt_hora': {'nombre': 'Kilowatt-hora', 'simbolo': 'kWh', 'factor': 3600000.0},
            'btu': {'nombre': 'BTU', 'simbolo': 'BTU', 'factor': 1055.06}
        }
    },
    'presion': {
        'nombre': 'Presión',
        'unidades': {
            'pascal': {'nombre': 'Pascal', 'simbolo': 'Pa', 'factor': 1.0},
            'kilopascal': {'nombre': 'Kilopascal', 'simbolo': 'kPa', 'factor': 1000.0},
            'bar': {'nombre': 'Bar', 'simbolo': 'bar', 'factor': 100000.0},
            'atmosfera': {'nombre': 'Atmósfera', 'simbolo': 'atm', 'factor': 101325.0},
            'mmhg': {'nombre': 'Milímetro de mercurio', 'simbolo': 'mmHg', 'factor': 133.322},
            'psi': {'nombre': 'Libra por pulgada cuadrada', 'simbolo': 'psi', 'factor': 6894.76}
        }
    },
    'velocidad': {
        'nombre': 'Velocidad',
        'unidades': {
            'metro_segundo': {'nombre': 'Metro por segundo', 'simbolo': 'm/s', 'factor': 1.0},
            'kilometro_hora': {'nombre': 'Kilómetro por hora', 'simbolo': 'km/h', 'factor': 0.277778},
            'milla_hora': {'nombre': 'Milla por hora', 'simbolo': 'mph', 'factor': 0.44704},
            'nudo': {'nombre': 'Nudo', 'simbolo': 'kn', 'factor': 0.514444},
            'pie_segundo': {'nombre': 'Pie por segundo', 'simbolo': 'ft/s', 'factor': 0.3048}
        }
    },
    'area': {
        'nombre': 'Área',
        'unidades': {
            'metro_cuadrado': {'nombre': 'Metro cuadrado', 'simbolo': 'm²', 'factor': 1.0},
            'kilometro_cuadrado': {'nombre': 'Kilómetro cuadrado', 'simbolo': 'km²', 'factor': 1000000.0},
            'centimetro_cuadrado': {'nombre': 'Centímetro cuadrado', 'simbolo': 'cm²', 'factor': 0.0001},
            'hectarea': {'nombre': 'Hectárea', 'simbolo': 'ha', 'factor': 10000.0},
            'acre': {'nombre': 'Acre', 'simbolo': 'ac', 'factor': 4046.86},
            'pie_cuadrado': {'nombre': 'Pie cuadrado', 'simbolo': 'ft²', 'factor': 0.092903},
            'pulgada_cuadrada': {'nombre': 'Pulgada cuadrada', 'simbolo': 'in²', 'factor': 0.00064516},
            'manzana': {'nombre': 'Manzana', 'simbolo': 'mz', 'factor': 7000.0}
        }
    },
    'tiempo': {
        'nombre': 'Tiempo',
        'unidades': {
            'segundo': {'nombre': 'Segundo', 'simbolo': 's', 'factor': 1.0},
            'minuto': {'nombre': 'Minuto', 'simbolo': 'min', 'factor': 60.0},
            'hora': {'nombre': 'Hora', 'simbolo': 'h', 'factor': 3600.0},
            'dia': {'nombre': 'Día', 'simbolo': 'd', 'factor': 86400.0},
            'semana': {'nombre': 'Semana', 'simbolo': 'sem', 'factor': 604800.0},
            'mes': {'nombre': 'Mes', 'simbolo': 'mes', 'factor': 2629746.0},
            'año': {'nombre': 'Año', 'simbolo': 'año', 'factor': 31556952.0}
        }
    }
}

def convertir_temperatura(valor: float, unidad_origen: str, unidad_destino: str) -> float:
    """Conversión especial para temperaturas"""
    # Convertir a Celsius primero
    if unidad_origen == 'fahrenheit':
        celsius = (valor - 32) * 5/9
    elif unidad_origen == 'kelvin':
        celsius = valor - 273.15
    elif unidad_origen == 'rankine':
        celsius = (valor - 491.67) * 5/9
    else:  # celsius
        celsius = valor
    
    # Convertir de Celsius a la unidad destino
    if unidad_destino == 'fahrenheit':
        return celsius * 9/5 + 32
    elif unidad_destino == 'kelvin':
        return celsius + 273.15
    elif unidad_destino == 'rankine':
        return celsius * 9/5 + 491.67
    else:  # celsius
        return celsius

@conversor_unidades_avanzado_bp.route('/api/obtener_categorias_unidades', methods=['GET'])
@login_required
def obtener_categorias_unidades():
    """API para obtener todas las categorías y unidades disponibles"""
    try:
        categorias = {}
        for categoria_id, categoria_data in UNIDADES_CONVERSION.items():
            categorias[categoria_id] = {
                'nombre': categoria_data['nombre'],
                'unidades': []
            }
            
            for unidad_id, unidad_data in categoria_data['unidades'].items():
                categorias[categoria_id]['unidades'].append({
                    'id': unidad_id,
                    'nombre': unidad_data['nombre'],
                    'simbolo': unidad_data['simbolo']
                })
        
        return jsonify({
            'success': True,
            'categorias': categorias
        })
        
    except Exception as e:
        print(f"❌ Error al obtener categorías: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@conversor_unidades_avanzado_bp.route('/api/convertir_unidades_avanzado', methods=['POST'])
@login_required
def convertir_unidades_avanzado():
    """API para convertir entre unidades de diferentes categorías"""
    try:
        data = request.get_json()
        valor = float(data.get('valor', 0))
        categoria = data.get('categoria', '')
        unidad_origen = data.get('unidad_origen', '')
        unidad_destino = data.get('unidad_destino', '')
        
        if not categoria or not unidad_origen or not unidad_destino:
            return jsonify({'error': 'Faltan parámetros requeridos'}), 400
        
        if categoria not in UNIDADES_CONVERSION:
            return jsonify({'error': 'Categoría no válida'}), 400
        
        categoria_data = UNIDADES_CONVERSION[categoria]
        
        if unidad_origen not in categoria_data['unidades'] or unidad_destino not in categoria_data['unidades']:
            return jsonify({'error': 'Unidad no válida'}), 400
        
        # Conversión especial para temperatura
        if categoria == 'temperatura':
            resultado = convertir_temperatura(valor, unidad_origen, unidad_destino)
        else:
            # Conversión estándar usando factores
            factor_origen = categoria_data['unidades'][unidad_origen]['factor']
            factor_destino = categoria_data['unidades'][unidad_destino]['factor']
            
            # Convertir a unidad base y luego a unidad destino
            valor_base = valor * factor_origen
            resultado = valor_base / factor_destino
        
        # Obtener información de las unidades
        unidad_origen_info = categoria_data['unidades'][unidad_origen]
        unidad_destino_info = categoria_data['unidades'][unidad_destino]
        
        return jsonify({
            'success': True,
            'valor_original': valor,
            'valor_convertido': resultado,
            'unidad_origen': {
                'nombre': unidad_origen_info['nombre'],
                'simbolo': unidad_origen_info['simbolo']
            },
            'unidad_destino': {
                'nombre': unidad_destino_info['nombre'],
                'simbolo': unidad_destino_info['simbolo']
            },
            'categoria': categoria_data['nombre'],
            'formula': f"Multiplicar el valor de {unidad_origen_info['nombre'].lower()} por {resultado/valor:.6f}" if valor != 0 else "N/A"
        })
        
    except ValueError:
        return jsonify({'error': 'Valor numérico no válido'}), 400
    except Exception as e:
        print(f"❌ Error en conversión: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@conversor_unidades_avanzado_bp.route('/api/conversiones_comunes/<categoria>', methods=['GET'])
@login_required
def obtener_conversiones_comunes(categoria):
    """API para obtener conversiones comunes de una categoría"""
    try:
        if categoria not in UNIDADES_CONVERSION:
            return jsonify({'error': 'Categoría no válida'}), 400
        
        conversiones_comunes = {
            'longitud': [
                {'de': 'metro', 'a': 'centimetro', 'ejemplo': '1 m = 100 cm'},
                {'de': 'kilometro', 'a': 'metro', 'ejemplo': '1 km = 1000 m'},
                {'de': 'pie', 'a': 'metro', 'ejemplo': '1 ft = 0.3048 m'},
                {'de': 'pulgada', 'a': 'centimetro', 'ejemplo': '1 in = 2.54 cm'}
            ],
            'masa': [
                {'de': 'kilogramo', 'a': 'libra', 'ejemplo': '1 kg = 2.205 lb'},
                {'de': 'gramo', 'a': 'onza', 'ejemplo': '1 g = 0.035 oz'},
                {'de': 'tonelada', 'a': 'kilogramo', 'ejemplo': '1 t = 1000 kg'},
                {'de': 'quintal', 'a': 'kilogramo', 'ejemplo': '1 q = 100 kg'}
            ],
            'volumen': [
                {'de': 'litro', 'a': 'galon_us', 'ejemplo': '1 L = 0.264 gal'},
                {'de': 'metro_cubico', 'a': 'litro', 'ejemplo': '1 m³ = 1000 L'},
                {'de': 'mililitro', 'a': 'onza_fluida', 'ejemplo': '1 mL = 0.034 fl oz'}
            ],
            'energia': [
                {'de': 'kilocaloria', 'a': 'megacaloria', 'ejemplo': '1000 kcal = 1 Mcal'},
                {'de': 'joule', 'a': 'caloria', 'ejemplo': '1 J = 0.239 cal'},
                {'de': 'kilowatt_hora', 'a': 'joule', 'ejemplo': '1 kWh = 3.6 MJ'}
            ]
        }
        
        return jsonify({
            'success': True,
            'categoria': UNIDADES_CONVERSION[categoria]['nombre'],
            'conversiones_comunes': conversiones_comunes.get(categoria, [])
        })
        
    except Exception as e:
        print(f"❌ Error al obtener conversiones comunes: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500
