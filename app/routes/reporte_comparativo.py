from flask import Blueprint, request, session, jsonify
from app.db import get_db_connection
from functools import wraps
from typing import Any

reporte_comparativo_bp = Blueprint('reporte_comparativo_bp', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'No autorizado'}), 401
        return f(*args, **kwargs)
    return decorated_function

def safe_float(value, default=0.0):
    """Convierte un valor a float de manera segura"""
    try:
        if value is None:
            return default
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_int(value, default=0):
    """Convierte un valor a entero de manera segura"""
    try:
        if value is None:
            return default
        return int(value)
    except (ValueError, TypeError):
        return default

def calcular_aportes_nutricionales(ingredientes):
    """Calcula los aportes nutricionales de una lista de ingredientes"""
    aportes = {
        'proteina_bruta': 0.0,
        'energia_metabolizable': 0.0,
        'fibra_bruta': 0.0,
        'grasa_bruta': 0.0,
        'cenizas': 0.0,
        'calcio': 0.0,
        'fosforo': 0.0,
        'lisina': 0.0,
        'metionina': 0.0
    }
    
    for ing in ingredientes:
        ing_typed: Any = ing
        porcentaje = safe_float(ing_typed.get('porcentaje', 0)) / 100
        
        aportes['proteina_bruta'] += safe_float(ing_typed.get('proteina_bruta', 0)) * porcentaje
        aportes['energia_metabolizable'] += safe_float(ing_typed.get('energia_metabolizable', 0)) * porcentaje
        aportes['fibra_bruta'] += safe_float(ing_typed.get('fibra_bruta', 0)) * porcentaje
        aportes['grasa_bruta'] += safe_float(ing_typed.get('grasa_bruta', 0)) * porcentaje
        aportes['cenizas'] += safe_float(ing_typed.get('cenizas', 0)) * porcentaje
        aportes['calcio'] += safe_float(ing_typed.get('calcio', 0)) * porcentaje
        aportes['fosforo'] += safe_float(ing_typed.get('fosforo', 0)) * porcentaje
        aportes['lisina'] += safe_float(ing_typed.get('lisina', 0)) * porcentaje
        aportes['metionina'] += safe_float(ing_typed.get('metionina', 0)) * porcentaje
    
    return aportes

def calcular_costo_formula(ingredientes):
    """Calcula el costo total de una fórmula"""
    costo_total = 0.0
    for ing in ingredientes:
        ing_typed: Any = ing
        porcentaje = safe_float(ing_typed.get('porcentaje', 0)) / 100
        precio = safe_float(ing_typed.get('precio', 0))
        costo_total += porcentaje * precio
    return costo_total

@reporte_comparativo_bp.route('/api/generar_reporte_comparativo_detallado', methods=['POST'])
@login_required
def generar_reporte_comparativo_detallado():
    """API para generar reporte comparativo detallado entre dos fórmulas"""
    try:
        data = request.get_json()
        formula_a_id = safe_int(data.get('formula_a_id'))
        formula_b_id = safe_int(data.get('formula_b_id'))
        nutrientes_seleccionados = data.get('nutrientes_seleccionados', [])
        consumo_analisis = safe_float(data.get('consumo_analisis', 3.0))
        incluir_costos = data.get('incluir_costos', True)
        mostrar_porcentajes = data.get('mostrar_porcentajes', True)
        
        if not formula_a_id or not formula_b_id or formula_a_id == formula_b_id:
            return jsonify({'error': 'Debe seleccionar dos fórmulas diferentes'}), 400
        
        if not nutrientes_seleccionados:
            return jsonify({'error': 'Debe seleccionar al menos un nutriente para comparar'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Obtener detalles de ambas fórmulas
        formulas_data = {}
        for formula_id, key in [(formula_a_id, 'A'), (formula_b_id, 'B')]:
            # Obtener información de la mezcla
            cursor.execute("""
                SELECT id, nombre, tipo_animales, etapa_produccion
                FROM mezclas 
                WHERE id = %s AND usuario_id = %s
            """, (formula_id, session['user_id']))
            
            mezcla = cursor.fetchone()
            if not mezcla:
                return jsonify({'error': f'Fórmula {key} no encontrada'}), 404
            
            # Obtener ingredientes con datos nutricionales
            cursor.execute("""
                SELECT mi.inclusion as porcentaje, 
                       i.id, i.nombre, i.precio, i.ms
                FROM mezcla_ingredientes mi
                JOIN ingredientes i ON mi.ingrediente_id = i.id
                WHERE mi.mezcla_id = %s
                ORDER BY mi.inclusion DESC
            """, (formula_id,))
            
            ingredientes_raw = cursor.fetchall()
            
            # Obtener datos nutricionales para cada ingrediente
            ingredientes = []
            for ing in ingredientes_raw:
                ing_typed: Any = ing
                ingrediente = {
                    'id': safe_int(ing_typed.get('id', 0)),
                    'nombre': ing_typed.get('nombre', ''),
                    'precio': safe_float(ing_typed.get('precio', 0.0)),
                    'ms': safe_float(ing_typed.get('ms', 100.0)),
                    'porcentaje': safe_float(ing_typed.get('porcentaje', 0.0)),
                    'proteina_bruta': 0.0,
                    'energia_metabolizable': 0.0,
                    'fibra_bruta': 0.0,
                    'grasa_bruta': 0.0,
                    'cenizas': 0.0,
                    'calcio': 0.0,
                    'fosforo': 0.0,
                    'lisina': 0.0,
                    'metionina': 0.0
                }
                
                # Obtener valores nutricionales específicos
                nutrientes_map = {
                    'Proteína Bruta': 'proteina_bruta',
                    'Energía Metabolizable': 'energia_metabolizable',
                    'Fibra Bruta': 'fibra_bruta',
                    'Grasa Bruta': 'grasa_bruta',
                    'Cenizas': 'cenizas',
                    'Calcio': 'calcio',
                    'Fósforo': 'fosforo',
                    'Lisina': 'lisina',
                    'Metionina': 'metionina'
                }
                
                for nutriente_nombre, campo in nutrientes_map.items():
                    cursor.execute("""
                        SELECT inut.valor
                        FROM ingredientes_nutrientes inut
                        JOIN nutrientes n ON inut.nutriente_id = n.id
                        WHERE inut.ingrediente_id = %s AND n.nombre = %s AND n.usuario_id = %s
                    """, (safe_int(ing_typed.get('id', 0)), nutriente_nombre, safe_int(session['user_id'])))
                    
                    result: Any = cursor.fetchone()
                    if result and result.get('valor') is not None:
                        ingrediente[campo] = safe_float(result.get('valor', 0.0))
                
                ingredientes.append(ingrediente)
            
            mezcla_typed: Any = mezcla
            formulas_data[key] = {
                'mezcla': {
                    'id': safe_int(mezcla_typed.get('id', 0)),
                    'nombre': mezcla_typed.get('nombre', ''),
                    'tipo_animales': mezcla_typed.get('tipo_animales', ''),
                    'etapa_produccion': mezcla_typed.get('etapa_produccion', '')
                },
                'ingredientes': ingredientes
            }
        
        cursor.close()
        conn.close()
        
        # Calcular aportes nutricionales
        aportes_a = calcular_aportes_nutricionales(formulas_data['A']['ingredientes'])
        aportes_b = calcular_aportes_nutricionales(formulas_data['B']['ingredientes'])
        
        # Generar comparación de nutrientes
        comparacion_nutrientes = []
        diferencias_significativas = []
        
        for nutriente in nutrientes_seleccionados:
            nutriente_id = nutriente.get('id', '')
            nutriente_nombre = nutriente.get('nombre', '')
            
            valor_a = aportes_a.get(nutriente_id, 0.0)
            valor_b = aportes_b.get(nutriente_id, 0.0)
            diferencia = valor_b - valor_a
            diferencia_porcentual = (diferencia / valor_a * 100) if valor_a > 0 else 0
            
            # Calcular aportes diarios
            aporte_a = (valor_a * consumo_analisis) / 100
            aporte_b = (valor_b * consumo_analisis) / 100
            diferencia_aporte = aporte_b - aporte_a
            
            comparacion_nutrientes.append({
                'nutriente': nutriente_nombre,
                'valor_a': valor_a,
                'valor_b': valor_b,
                'diferencia': diferencia,
                'diferencia_porcentual': diferencia_porcentual,
                'aporte_a': aporte_a,
                'aporte_b': aporte_b,
                'diferencia_aporte': diferencia_aporte
            })
            
            # Identificar diferencias significativas
            if abs(diferencia_porcentual) > 5:
                diferencias_significativas.append({
                    'nutriente': nutriente_nombre,
                    'diferencia_porcentual': diferencia_porcentual,
                    'significativa': abs(diferencia_porcentual) > 10
                })
        
        # Análisis de costos
        analisis_costos = None
        if incluir_costos:
            costo_a = calcular_costo_formula(formulas_data['A']['ingredientes'])
            costo_b = calcular_costo_formula(formulas_data['B']['ingredientes'])
            diferencia_costo = costo_b - costo_a
            diferencia_costo_porcentual = (diferencia_costo / costo_a * 100) if costo_a > 0 else 0
            
            analisis_costos = {
                'costo_a': costo_a,
                'costo_b': costo_b,
                'diferencia_costo': diferencia_costo,
                'diferencia_costo_porcentual': diferencia_costo_porcentual,
                'costo_animal_dia_a': costo_a * consumo_analisis,
                'costo_animal_dia_b': costo_b * consumo_analisis
            }
        
        return jsonify({
            'success': True,
            'formula_a': formulas_data['A']['mezcla'],
            'formula_b': formulas_data['B']['mezcla'],
            'parametros': {
                'consumo_analisis': consumo_analisis,
                'incluir_costos': incluir_costos,
                'mostrar_porcentajes': mostrar_porcentajes
            },
            'comparacion_nutrientes': comparacion_nutrientes,
            'diferencias_significativas': diferencias_significativas,
            'analisis_costos': analisis_costos
        })
        
    except Exception as e:
        print(f"❌ Error en reporte comparativo: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500
