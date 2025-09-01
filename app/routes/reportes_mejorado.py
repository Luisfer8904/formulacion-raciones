from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, make_response
from functools import wraps
from datetime import datetime
import json
import os
import io

# Importar ReportLab de forma condicional para evitar errores
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠️ ReportLab no disponible, usando generación de texto plano")

from app.db import get_db_connection

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
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, nombre, tipo_animales as especie, etapa_produccion as tipo_plan,
                   DATE_FORMAT(fecha_creacion, '%Y-%m-%d') as fecha_creacion,
                   costo_total as costo_kg
            FROM mezclas 
            WHERE usuario_id = %s 
            ORDER BY fecha_creacion DESC
        """, (session['user_id'],))
        
        mezclas = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Si no hay mezclas reales, usar datos de ejemplo
        if not mezclas:
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
        print(f"❌ Error al obtener mezclas: {e}")
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
            'url_vista_previa': f'/api/ver_reporte/{reporte["id"]}',
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
    """Genera PDF usando ReportLab si está disponible, sino texto plano"""
    
    if REPORTLAB_AVAILABLE:
        try:
            # Crear buffer en memoria
            buffer = io.BytesIO()
            
            # Crear documento PDF
            doc = SimpleDocTemplate(buffer, pagesize=A4, 
                                  rightMargin=72, leftMargin=72,
                                  topMargin=72, bottomMargin=18)
            
            # Obtener estilos
            styles = getSampleStyleSheet()
            
            # Crear estilos personalizados
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#2c3e50')
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=12,
                textColor=colors.HexColor('#7CB342')
            )
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=6
            )
            
            # Contenido del PDF
            story = []
            
            # Título
            story.append(Paragraph("REPORTE COMPARATIVO DE FÓRMULAS", title_style))
            story.append(Spacer(1, 12))
            
            # Información del reporte
            info_data = [
                ['ID del Reporte:', reporte['id']],
                ['Fecha de Generación:', datetime.fromisoformat(reporte['fecha_generacion']).strftime('%d/%m/%Y %H:%M:%S')],
                ['Cliente:', reporte.get('cliente', 'No especificado')],
                ['Observaciones:', reporte.get('observaciones', 'Ninguna')]
            ]
            
            info_table = Table(info_data, colWidths=[2*inch, 4*inch])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            
            story.append(info_table)
            story.append(Spacer(1, 20))
            
            # Comparación de fórmulas
            story.append(Paragraph("COMPARACIÓN DE FÓRMULAS", heading_style))
            
            formula_data = [
                ['Característica', 'Fórmula A', 'Fórmula B'],
                ['Nombre', reporte['formula_a']['nombre'], reporte['formula_b']['nombre']],
                ['Especie', reporte['formula_a']['especie'], reporte['formula_b']['especie']],
                ['Costo/kg', f"${reporte['formula_a']['costo_kg']:.3f}", f"${reporte['formula_b']['costo_kg']:.3f}"]
            ]
            
            formula_table = Table(formula_data, colWidths=[2*inch, 2*inch, 2*inch])
            formula_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7CB342')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ]))
            
            story.append(formula_table)
            story.append(Spacer(1, 20))
            
            # Análisis de costos
            story.append(Paragraph("ANÁLISIS DE COSTOS", heading_style))
            
            costo_data = [
                ['Métrica', 'Valor'],
                ['Diferencia Absoluta', f"${reporte['analisis']['costo']['diferencia_absoluta']:.3f}"],
                ['Diferencia Porcentual', f"{reporte['analisis']['costo']['diferencia_porcentual']:.1f}%"]
            ]
            
            costo_table = Table(costo_data, colWidths=[3*inch, 2*inch])
            costo_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#17a2b8')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            story.append(costo_table)
            story.append(Spacer(1, 20))
            
            # Análisis nutricional
            if 'nutrientes' in reporte['analisis']:
                story.append(Paragraph("ANÁLISIS NUTRICIONAL", heading_style))
                
                nutriente_data = [['Nutriente', 'Fórmula A', 'Fórmula B', 'Diferencia', 'Porcentaje']]
                
                for nutriente, valores in reporte['analisis']['nutrientes'].items():
                    nutriente_data.append([
                        nutriente.capitalize(),
                        f"{valores['formula_a']:.2f}",
                        f"{valores['formula_b']:.2f}",
                        f"{valores['diferencia']:.2f}",
                        f"{valores['porcentaje']:.1f}%"
                    ])
                
                nutriente_table = Table(nutriente_data, colWidths=[1.2*inch, 1*inch, 1*inch, 1*inch, 1*inch])
                nutriente_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#28a745')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                
                story.append(nutriente_table)
                story.append(Spacer(1, 20))
            
            # Conclusiones
            story.append(Paragraph("CONCLUSIONES", heading_style))
            
            for i, conclusion in enumerate(reporte['analisis']['conclusiones'], 1):
                story.append(Paragraph(f"{i}. {conclusion}", normal_style))
            
            story.append(Spacer(1, 12))
            
            # Recomendación
            story.append(Paragraph("RECOMENDACIÓN", heading_style))
            story.append(Paragraph(reporte['analisis']['recomendacion'], normal_style))
            
            # Pie de página
            story.append(Spacer(1, 30))
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                alignment=TA_CENTER,
                textColor=colors.grey
            )
            story.append(Paragraph("Generado por FeedPro - Sistema de Formulación Nutricional", footer_style))
            
            # Construir PDF
            doc.build(story)
            
            # Obtener contenido del buffer
            pdf_content = buffer.getvalue()
            buffer.close()
            
            return pdf_content
            
        except Exception as e:
            print(f"❌ Error al generar PDF con ReportLab: {e}")
            # Fallback a texto plano
            pass
    
    # Generar reporte en texto plano como fallback
    try:
        fecha_formateada = datetime.fromisoformat(reporte['fecha_generacion']).strftime('%d/%m/%Y %H:%M:%S')
    except:
        fecha_formateada = reporte['fecha_generacion']
    
    contenido_texto = f"""
REPORTE COMPARATIVO DE FÓRMULAS
================================

ID del Reporte: {reporte['id']}
Fecha de Generación: {fecha_formateada}
Cliente: {reporte.get('cliente', 'No especificado')}
Observaciones: {reporte.get('observaciones', 'Ninguna')}

COMPARACIÓN DE FÓRMULAS
=======================

Fórmula A: {reporte['formula_a']['nombre']}
- Especie: {reporte['formula_a']['especie']}
- Costo/kg: ${reporte['formula_a']['costo_kg']:.3f}

Fórmula B: {reporte['formula_b']['nombre']}
- Especie: {reporte['formula_b']['especie']}
- Costo/kg: ${reporte['formula_b']['costo_kg']:.3f}

ANÁLISIS DE COSTOS
==================

Diferencia Absoluta: ${reporte['analisis']['costo']['diferencia_absoluta']:.3f}
Diferencia Porcentual: {reporte['analisis']['costo']['diferencia_porcentual']:.1f}%

ANÁLISIS NUTRICIONAL
====================
"""
    
    if 'nutrientes' in reporte['analisis']:
        for nutriente, valores in reporte['analisis']['nutrientes'].items():
            contenido_texto += f"""
{nutriente.capitalize()}:
- Fórmula A: {valores['formula_a']:.2f}
- Fórmula B: {valores['formula_b']:.2f}
- Diferencia: {valores['diferencia']:.2f}
- Porcentaje: {valores['porcentaje']:.1f}%
"""
    
    contenido_texto += f"""

CONCLUSIONES
============
"""
    
    for i, conclusion in enumerate(reporte['analisis']['conclusiones'], 1):
        contenido_texto += f"{i}. {conclusion}\n"
    
    contenido_texto += f"""

RECOMENDACIÓN
=============
{reporte['analisis']['recomendacion']}

---
Generado por FeedPro - Sistema de Formulación Nutricional
"""
    
    return contenido_texto.encode('utf-8')

@reportes_mejorado_bp.route('/api/ver_reporte/<reporte_id>')
@login_required
def ver_reporte(reporte_id):
    """Ver reporte en el navegador (vista previa)"""
    try:
        # Crear reporte de ejemplo para vista previa
        reporte_ejemplo = {
            'id': reporte_id,
            'fecha_generacion': datetime.now().isoformat(),
            'cliente': 'Cliente de Ejemplo',
            'observaciones': 'Reporte generado para vista previa',
            'formula_a': {
                'nombre': 'Fórmula A - Ejemplo',
                'especie': 'Pollo',
                'costo_kg': 1.25
            },
            'formula_b': {
                'nombre': 'Fórmula B - Ejemplo',
                'especie': 'Cerdo',
                'costo_kg': 1.45
            },
            'analisis': {
                'costo': {
                    'diferencia_absoluta': 0.20,
                    'diferencia_porcentual': 16.0
                },
                'nutrientes': {
                    'proteina': {
                        'formula_a': 22.5,
                        'formula_b': 18.5,
                        'diferencia': -4.0,
                        'porcentaje': -17.8
                    },
                    'energia': {
                        'formula_a': 3100,
                        'formula_b': 3250,
                        'diferencia': 150,
                        'porcentaje': 4.8
                    }
                },
                'conclusiones': [
                    'La Fórmula B es 16.0% más costosa que la Fórmula A',
                    'La Fórmula A tiene significativamente más proteína',
                    'La Fórmula B proporciona mayor energía'
                ],
                'recomendacion': 'Se recomienda evaluar si el costo adicional de la Fórmula B justifica sus beneficios'
            }
        }
        
        # Generar contenido del reporte
        contenido_reporte = generar_pdf_basico(reporte_ejemplo)
        
        # Crear respuesta para vista previa en navegador
        response = make_response(contenido_reporte)
        
        if REPORTLAB_AVAILABLE and isinstance(contenido_reporte, bytes) and len(contenido_reporte) > 100:
            # Es un PDF real - mostrar en navegador
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'inline; filename=reporte_comparativo_{reporte_id}.pdf'
        else:
            # Es texto plano - mostrar en navegador
            response.headers['Content-Type'] = 'text/plain; charset=utf-8'
            response.headers['Content-Disposition'] = f'inline; filename=reporte_comparativo_{reporte_id}.txt'
        
        return response
        
    except Exception as e:
        print(f"❌ Error al mostrar reporte: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@reportes_mejorado_bp.route('/api/descargar_reporte/<reporte_id>')
@login_required
def descargar_reporte(reporte_id):
    """Descargar reporte en formato PDF o texto"""
    try:
        # Crear reporte de ejemplo para descarga
        reporte_ejemplo = {
            'id': reporte_id,
            'fecha_generacion': datetime.now().isoformat(),
            'cliente': 'Cliente de Ejemplo',
            'observaciones': 'Reporte generado para descarga',
            'formula_a': {
                'nombre': 'Fórmula A - Ejemplo',
                'especie': 'Pollo',
                'costo_kg': 1.25
            },
            'formula_b': {
                'nombre': 'Fórmula B - Ejemplo',
                'especie': 'Cerdo',
                'costo_kg': 1.45
            },
            'analisis': {
                'costo': {
                    'diferencia_absoluta': 0.20,
                    'diferencia_porcentual': 16.0
                },
                'nutrientes': {
                    'proteina': {
                        'formula_a': 22.5,
                        'formula_b': 18.5,
                        'diferencia': -4.0,
                        'porcentaje': -17.8
                    },
                    'energia': {
                        'formula_a': 3100,
                        'formula_b': 3250,
                        'diferencia': 150,
                        'porcentaje': 4.8
                    }
                },
                'conclusiones': [
                    'La Fórmula B es 16.0% más costosa que la Fórmula A',
                    'La Fórmula A tiene significativamente más proteína',
                    'La Fórmula B proporciona mayor energía'
                ],
                'recomendacion': 'Se recomienda evaluar si el costo adicional de la Fórmula B justifica sus beneficios'
            }
        }
        
        # Generar contenido del reporte
        contenido_reporte = generar_pdf_basico(reporte_ejemplo)
        
        # Crear respuesta para descarga forzada
        response = make_response(contenido_reporte)
        
        if REPORTLAB_AVAILABLE and isinstance(contenido_reporte, bytes) and len(contenido_reporte) > 100:
            # Es un PDF real - forzar descarga
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'attachment; filename=reporte_comparativo_{reporte_id}.pdf'
        else:
            # Es texto plano - forzar descarga
            response.headers['Content-Type'] = 'text/plain; charset=utf-8'
            response.headers['Content-Disposition'] = f'attachment; filename=reporte_comparativo_{reporte_id}.txt'
        
        return response
        
    except Exception as e:
        print(f"❌ Error al descargar reporte: {e}")
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
