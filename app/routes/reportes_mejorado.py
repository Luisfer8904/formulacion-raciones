from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, make_response
from functools import wraps
from datetime import datetime
import json
import os

reportes_mejorado_bp = Blueprint('reportes_mejorado_bp', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth_bp.login'))
        return f(*args, **kwargs)
    return decorated_function

@reportes_mejorado_bp.route('/reportes')
@login_required
def reportes():
    """Página principal de reportes"""
    return render_template('operaciones/reportes.html')

@reportes_mejorado_bp.route('/api/mezclas_usuario', methods=['GET'])
@login_required
def obtener_mezclas_usuario():
    """API para obtener las mezclas del usuario"""
    try:
        # Datos simulados de mezclas
        mezclas = [
            {
                'id': 1,
                'nombre': 'Pollo Engorde Inicial',
                'especie': 'Pollo',
                'tipo_plan': 'Engorde',
                'fecha_creacion': '2024-01-10',
                'costo_kg': 1.25
            },
            {
                'id': 2,
                'nombre': 'Cerdo Crecimiento Premium',
                'especie': 'Cerdo',
                'tipo_plan': 'Crecimiento',
                'fecha_creacion': '2024-01-12',
                'costo_kg': 1.45
            },
            {
                'id': 3,
                'nombre': 'Gallina Postura Comercial',
                'especie': 'Gallina',
                'tipo_plan': 'Postura',
                'fecha_creacion': '2024-01-15',
                'costo_kg': 1.35
            },
            {
                'id': 4,
                'nombre': 'Bovino Engorde Intensivo',
                'especie': 'Bovino',
                'tipo_plan': 'Engorde',
                'fecha_creacion': '2024-01-18',
                'costo_kg': 1.55
            }
        ]
        
        return jsonify({
            'success': True,
            'mezclas': mezclas
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@reportes_mejorado_bp.route('/api/generar_reporte_comparativo', methods=['POST'])
@login_required
def generar_reporte_comparativo():
    """API para generar reporte comparativo entre dos fórmulas"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        formula_a_id = data.get('formula_a')
        formula_b_id = data.get('formula_b')
        
        if not formula_a_id or not formula_b_id:
            return jsonify({
                'success': False,
                'error': 'Debe seleccionar ambas fórmulas'
            }), 400
        
        if formula_a_id == formula_b_id:
            return jsonify({
                'success': False,
                'error': 'Debe seleccionar fórmulas diferentes'
            }), 400
        
        # Obtener datos de las fórmulas (simulado)
        formulas_data = {
            '1': {
                'nombre': 'Pollo Engorde Inicial',
                'especie': 'Pollo',
                'costo_kg': 1.25,
                'ingredientes': [
                    {'nombre': 'Maíz Amarillo', 'porcentaje': 55.0, 'costo': 0.68},
                    {'nombre': 'Soya Integral', 'porcentaje': 25.0, 'costo': 0.38},
                    {'nombre': 'Harina de Pescado', 'porcentaje': 8.0, 'costo': 0.12},
                    {'nombre': 'Aceite de Soya', 'porcentaje': 3.0, 'costo': 0.05},
                    {'nombre': 'Premezcla Vitamínica', 'porcentaje': 2.0, 'costo': 0.02}
                ],
                'nutrientes': {
                    'proteina': 22.5,
                    'energia': 3100,
                    'fibra': 3.2,
                    'grasa': 5.8,
                    'calcio': 1.0,
                    'fosforo': 0.7
                }
            },
            '2': {
                'nombre': 'Cerdo Crecimiento Premium',
                'especie': 'Cerdo',
                'costo_kg': 1.45,
                'ingredientes': [
                    {'nombre': 'Maíz Amarillo', 'porcentaje': 60.0, 'costo': 0.87},
                    {'nombre': 'Soya Integral', 'porcentaje': 20.0, 'costo': 0.29},
                    {'nombre': 'Harina de Pescado', 'porcentaje': 10.0, 'costo': 0.15},
                    {'nombre': 'Aceite de Palma', 'porcentaje': 4.0, 'costo': 0.06},
                    {'nombre': 'Premezcla Mineral', 'porcentaje': 3.0, 'costo': 0.08}
                ],
                'nutrientes': {
                    'proteina': 18.5,
                    'energia': 3250,
                    'fibra': 2.8,
                    'grasa': 6.2,
                    'calcio': 0.8,
                    'fosforo': 0.6
                }
            },
            '3': {
                'nombre': 'Gallina Postura Comercial',
                'especie': 'Gallina',
                'costo_kg': 1.35,
                'ingredientes': [
                    {'nombre': 'Maíz Amarillo', 'porcentaje': 50.0, 'costo': 0.68},
                    {'nombre': 'Soya Integral', 'porcentaje': 28.0, 'costo': 0.38},
                    {'nombre': 'Carbonato de Calcio', 'porcentaje': 8.0, 'costo': 0.08},
                    {'nombre': 'Harina de Pescado', 'porcentaje': 6.0, 'costo': 0.12},
                    {'nombre': 'Aceite de Soya', 'porcentaje': 2.5, 'costo': 0.04}
                ],
                'nutrientes': {
                    'proteina': 16.8,
                    'energia': 2850,
                    'fibra': 3.5,
                    'grasa': 4.2,
                    'calcio': 3.8,
                    'fosforo': 0.65
                }
            },
            '4': {
                'nombre': 'Bovino Engorde Intensivo',
                'especie': 'Bovino',
                'costo_kg': 1.55,
                'ingredientes': [
                    {'nombre': 'Maíz Amarillo', 'porcentaje': 45.0, 'costo': 0.70},
                    {'nombre': 'Soya Integral', 'porcentaje': 15.0, 'costo': 0.23},
                    {'nombre': 'Melaza', 'porcentaje': 12.0, 'costo': 0.14},
                    {'nombre': 'Heno de Alfalfa', 'porcentaje': 20.0, 'costo': 0.32},
                    {'nombre': 'Urea', 'porcentaje': 3.0, 'costo': 0.06}
                ],
                'nutrientes': {
                    'proteina': 14.2,
                    'energia': 2950,
                    'fibra': 12.5,
                    'grasa': 3.8,
                    'calcio': 0.6,
                    'fosforo': 0.4
                }
            }
        }
        
        formula_a = formulas_data.get(str(formula_a_id))
        formula_b = formulas_data.get(str(formula_b_id))
        
        if not formula_a or not formula_b:
            return jsonify({
                'success': False,
                'error': 'Fórmula no encontrada'
            }), 404
        
        # Generar análisis comparativo
        analisis = generar_analisis_comparativo(formula_a, formula_b)
        
        # Crear reporte
        reporte = {
            'id': f'RC-{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'fecha_generacion': datetime.now().isoformat(),
            'cliente': data.get('cliente', ''),
            'observaciones': data.get('observaciones', ''),
            'opciones': {
                'incluir_graficos': data.get('incluir_graficos', True),
                'generar_conclusion': data.get('generar_conclusion', True),
                'analisis_costos': data.get('analisis_costos', True)
            },
            'formula_a': formula_a,
            'formula_b': formula_b,
            'analisis': analisis
        }
        
        # Generar PDF básico (simulado)
        pdf_content = generar_pdf_basico(reporte)
        
        return jsonify({
            'success': True,
            'mensaje': 'Reporte generado exitosamente',
            'reporte': reporte,
            'pdf_disponible': True,
            'url_descarga': f'/api/descargar_reporte/{reporte["id"]}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def generar_analisis_comparativo(formula_a, formula_b):
    """Genera análisis comparativo entre dos fórmulas"""
    
    # Comparación de costos
    diferencia_costo = formula_b['costo_kg'] - formula_a['costo_kg']
    porcentaje_costo = (diferencia_costo / formula_a['costo_kg']) * 100
    
    # Comparación nutricional
    comparacion_nutrientes = {}
    for nutriente in formula_a['nutrientes']:
        valor_a = formula_a['nutrientes'][nutriente]
        valor_b = formula_b['nutrientes'][nutriente]
        diferencia = valor_b - valor_a
        porcentaje = (diferencia / valor_a) * 100 if valor_a > 0 else 0
        
        comparacion_nutrientes[nutriente] = {
            'formula_a': valor_a,
            'formula_b': valor_b,
            'diferencia': round(diferencia, 2),
            'porcentaje': round(porcentaje, 1)
        }
    
    # Generar conclusiones automáticas
    conclusiones = []
    
    if abs(porcentaje_costo) > 5:
        if porcentaje_costo > 0:
            conclusiones.append(f"La Fórmula B es {abs(porcentaje_costo):.1f}% más costosa que la Fórmula A")
        else:
            conclusiones.append(f"La Fórmula B es {abs(porcentaje_costo):.1f}% más económica que la Fórmula A")
    
    # Análisis nutricional
    if comparacion_nutrientes['proteina']['porcentaje'] > 10:
        conclusiones.append("La Fórmula B tiene significativamente más proteína")
    elif comparacion_nutrientes['proteina']['porcentaje'] < -10:
        conclusiones.append("La Fórmula A tiene significativamente más proteína")
    
    if comparacion_nutrientes['energia']['porcentaje'] > 5:
        conclusiones.append("La Fórmula B proporciona mayor energía")
    elif comparacion_nutrientes['energia']['porcentaje'] < -5:
        conclusiones.append("La Fórmula A proporciona mayor energía")
    
    # Recomendación general
    if porcentaje_costo < 0 and comparacion_nutrientes['proteina']['porcentaje'] >= 0:
        recomendacion = "Se recomienda la Fórmula B por mejor relación costo-beneficio"
    elif porcentaje_costo > 10:
        recomendacion = "Se recomienda evaluar si el costo adicional de la Fórmula B justifica sus beneficios"
    else:
        recomendacion = "Ambas fórmulas son viables, la elección depende de objetivos específicos"
    
    return {
        'costo': {
            'diferencia_absoluta': round(diferencia_costo, 3),
            'diferencia_porcentual': round(porcentaje_costo, 1)
        },
        'nutrientes': comparacion_nutrientes,
        'conclusiones': conclusiones,
        'recomendacion': recomendacion
    }

def generar_pdf_basico(reporte):
    """Genera contenido PDF básico (simulado)"""
    # En una implementación real, aquí usarías una librería como ReportLab
    # Por ahora, simulamos la generación
    
    pdf_content = f"""
    REPORTE COMPARATIVO DE FÓRMULAS
    ================================
    
    ID: {reporte['id']}
    Fecha: {reporte['fecha_generacion']}
    Cliente: {reporte.get('cliente', 'N/A')}
    
    FÓRMULA A: {reporte['formula_a']['nombre']}
    - Especie: {reporte['formula_a']['especie']}
    - Costo/kg: ${reporte['formula_a']['costo_kg']:.3f}
    
    FÓRMULA B: {reporte['formula_b']['nombre']}
    - Especie: {reporte['formula_b']['especie']}
    - Costo/kg: ${reporte['formula_b']['costo_kg']:.3f}
    
    ANÁLISIS DE COSTOS:
    - Diferencia: ${reporte['analisis']['costo']['diferencia_absoluta']:.3f}
    - Porcentaje: {reporte['analisis']['costo']['diferencia_porcentual']:.1f}%
    
    CONCLUSIONES:
    {chr(10).join('- ' + c for c in reporte['analisis']['conclusiones'])}
    
    RECOMENDACIÓN:
    {reporte['analisis']['recomendacion']}
    """
    
    return pdf_content

@reportes_mejorado_bp.route('/api/descargar_reporte/<reporte_id>')
@login_required
def descargar_reporte(reporte_id):
    """Descargar reporte en formato PDF"""
    try:
        # En una implementación real, buscarías el reporte en la base de datos
        # Por ahora, generamos contenido simulado
        
        contenido_pdf = f"""
        REPORTE COMPARATIVO - {reporte_id}
        Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}
        
        Este es un reporte de ejemplo generado por FeedPro.
        En una implementación completa, aquí estaría el contenido
        detallado del análisis comparativo entre las fórmulas seleccionadas.
        """
        
        response = make_response(contenido_pdf)
        response.headers['Content-Type'] = 'text/plain'
        response.headers['Content-Disposition'] = f'attachment; filename=reporte_{reporte_id}.txt'
        
        return response
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@reportes_mejorado_bp.route('/api/historial_reportes', methods=['GET'])
@login_required
def obtener_historial_reportes():
    """API para obtener historial de reportes generados"""
    try:
        # Datos simulados de historial
        historial = [
            {
                'id': 'RC-20240115143022',
                'tipo': 'Comparativo',
                'fecha': '2024-01-15 14:30',
                'formulas': ['Pollo Engorde Inicial', 'Cerdo Crecimiento'],
                'estado': 'Completado'
            },
            {
                'id': 'RC-20240114091545',
                'tipo': 'Comparativo',
                'fecha': '2024-01-14 09:15',
                'formulas': ['Gallina Postura', 'Bovino Engorde'],
                'estado': 'Completado'
            }
        ]
        
        return jsonify({
            'success': True,
            'historial': historial
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
