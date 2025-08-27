from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
from datetime import datetime, timedelta

planificador_bp = Blueprint('planificador_bp', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@planificador_bp.route('/planificador')
@login_required
def planificador():
    """Página principal del planificador de producción"""
    return render_template('operaciones/planificador.html')

@planificador_bp.route('/api/bachadas', methods=['GET'])
@login_required
def obtener_bachadas():
    """API para obtener lista de bachadas"""
    try:
        # Datos simulados de bachadas
        bachadas = [
            {
                'id': 'BCH-001',
                'formula': 'Pollo Engorde Inicial',
                'cantidad': 500,
                'fecha_programada': '2024-01-15 14:00',
                'estado': 'En Proceso',
                'observaciones': 'Bachada prioritaria'
            },
            {
                'id': 'BCH-002',
                'formula': 'Cerdo Crecimiento',
                'cantidad': 750,
                'fecha_programada': '2024-01-16 09:00',
                'estado': 'Programada',
                'observaciones': 'Cliente especial'
            },
            {
                'id': 'BCH-003',
                'formula': 'Gallina Postura',
                'cantidad': 300,
                'fecha_programada': '2024-01-17 11:00',
                'estado': 'Pendiente',
                'observaciones': ''
            }
        ]
        
        return jsonify({
            'success': True,
            'bachadas': bachadas,
            'total': len(bachadas)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@planificador_bp.route('/api/bachadas', methods=['POST'])
@login_required
def crear_bachada():
    """API para crear nueva bachada"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        campos_requeridos = ['codigo', 'formula', 'cantidad', 'fecha_programada']
        for campo in campos_requeridos:
            if not data.get(campo):
                return jsonify({
                    'success': False,
                    'error': f'Campo requerido: {campo}'
                }), 400
        
        # Validar cantidad
        cantidad = float(data.get('cantidad', 0))
        if cantidad <= 0:
            return jsonify({
                'success': False,
                'error': 'La cantidad debe ser mayor a 0'
            }), 400
        
        # Validar fecha
        try:
            fecha_programada = datetime.fromisoformat(data.get('fecha_programada'))
            if fecha_programada < datetime.now():
                return jsonify({
                    'success': False,
                    'error': 'La fecha programada no puede ser en el pasado'
                }), 400
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Formato de fecha inválido'
            }), 400
        
        # Simular creación de bachada
        nueva_bachada = {
            'id': data.get('codigo'),
            'formula': data.get('formula'),
            'cantidad': cantidad,
            'fecha_programada': data.get('fecha_programada'),
            'estado': 'Programada',
            'observaciones': data.get('observaciones', ''),
            'fecha_creacion': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'mensaje': 'Bachada creada exitosamente',
            'bachada': nueva_bachada
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@planificador_bp.route('/api/bachadas/<bachada_id>/completar', methods=['POST'])
@login_required
def completar_bachada(bachada_id):
    """API para marcar bachada como completada"""
    try:
        data = request.get_json() or {}
        
        # Simular completar bachada
        resultado = {
            'id': bachada_id,
            'estado': 'Completada',
            'fecha_completada': datetime.now().isoformat(),
            'observaciones_finales': data.get('observaciones', '')
        }
        
        return jsonify({
            'success': True,
            'mensaje': f'Bachada {bachada_id} completada exitosamente',
            'bachada': resultado
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@planificador_bp.route('/api/inventario/alertas', methods=['GET'])
@login_required
def obtener_alertas_inventario():
    """API para obtener alertas de inventario"""
    try:
        # Datos simulados de alertas
        alertas = [
            {
                'ingrediente': 'Maíz Amarillo',
                'stock_actual': 150,
                'stock_minimo': 200,
                'unidad': 'kg',
                'tipo': 'warning',
                'mensaje': 'Stock bajo'
            },
            {
                'ingrediente': 'Harina de Pescado',
                'stock_actual': 0,
                'stock_minimo': 100,
                'unidad': 'kg',
                'tipo': 'danger',
                'mensaje': 'Agotado - Reposición urgente'
            },
            {
                'ingrediente': 'Soya Integral',
                'stock_actual': 500,
                'stock_minimo': 300,
                'unidad': 'kg',
                'tipo': 'info',
                'mensaje': 'Entrega programada mañana'
            }
        ]
        
        return jsonify({
            'success': True,
            'alertas': alertas,
            'total_alertas': len(alertas)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@planificador_bp.route('/api/eficiencia/semanal', methods=['GET'])
@login_required
def obtener_eficiencia_semanal():
    """API para obtener datos de eficiencia semanal"""
    try:
        # Datos simulados de eficiencia
        eficiencia = {
            'lunes': 92,
            'martes': 96,
            'miercoles': 89,
            'jueves': 94,
            'viernes': 98,
            'sabado': 91,
            'domingo': 87
        }
        
        promedio = sum(eficiencia.values()) / len(eficiencia)
        
        return jsonify({
            'success': True,
            'eficiencia_diaria': eficiencia,
            'promedio_semanal': round(promedio, 1),
            'tendencia': 'positiva' if promedio > 90 else 'negativa'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@planificador_bp.route('/api/estadisticas/produccion', methods=['GET'])
@login_required
def obtener_estadisticas_produccion():
    """API para obtener estadísticas de producción"""
    try:
        # Datos simulados
        estadisticas = {
            'bachadas_activas': 3,
            'inventario_total': 2450,
            'tiempo_promedio': 4.2,
            'eficiencia_general': 94.5,
            'produccion_semanal': 15750,
            'meta_semanal': 16000,
            'porcentaje_meta': 98.4
        }
        
        return jsonify({
            'success': True,
            'estadisticas': estadisticas
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@planificador_bp.route('/api/recursos/disponibilidad', methods=['GET'])
@login_required
def obtener_disponibilidad_recursos():
    """API para obtener disponibilidad de recursos"""
    try:
        # Datos simulados de recursos
        recursos = {
            'personal': {
                'disponible': 8,
                'total': 10,
                'porcentaje': 80
            },
            'equipos': {
                'operativos': 4,
                'total': 5,
                'porcentaje': 80,
                'en_mantenimiento': 1
            },
            'lineas_produccion': {
                'activas': 2,
                'total': 3,
                'porcentaje': 67,
                'disponibles': 1
            }
        }
        
        return jsonify({
            'success': True,
            'recursos': recursos
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@planificador_bp.route('/api/reportes/produccion', methods=['POST'])
@login_required
def generar_reporte_produccion():
    """API para generar reportes de producción"""
    try:
        data = request.get_json()
        tipo_reporte = data.get('tipo', 'general')
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        
        # Simular generación de reporte
        reporte = {
            'id': f'RPT-{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'tipo': tipo_reporte,
            'fecha_generacion': datetime.now().isoformat(),
            'periodo': {
                'inicio': fecha_inicio,
                'fin': fecha_fin
            },
            'datos': {
                'bachadas_completadas': 15,
                'produccion_total': 7850,
                'eficiencia_promedio': 94.2,
                'tiempo_total': 63.5
            }
        }
        
        return jsonify({
            'success': True,
            'mensaje': 'Reporte generado exitosamente',
            'reporte': reporte
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
