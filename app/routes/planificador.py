from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
from datetime import datetime, timedelta
from app.db import get_db_connection

planificador_bp = Blueprint('planificador_bp', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth_bp.login'))
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
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Obtener bachadas del usuario
        cursor.execute("""
            SELECT 
                id,
                codigo,
                nombre,
                formula_nombre,
                cantidad_programada,
                cantidad_producida,
                DATE_FORMAT(fecha_programada, '%Y-%m-%d %H:%i') as fecha_programada,
                DATE_FORMAT(fecha_inicio, '%Y-%m-%d %H:%i') as fecha_inicio,
                DATE_FORMAT(fecha_completada, '%Y-%m-%d %H:%i') as fecha_completada,
                estado,
                prioridad,
                observaciones,
                tiempo_estimado,
                tiempo_real,
                eficiencia,
                costo_estimado,
                costo_real
            FROM bachadas 
            WHERE usuario_id = %s 
            ORDER BY fecha_programada ASC
        """, (session['user_id'],))
        
        bachadas = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Si no hay bachadas reales, usar datos de ejemplo
        if not bachadas:
            bachadas = [
                {
                    'id': 1,
                    'codigo': 'BCH-001',
                    'nombre': 'Pollo Engorde Inicial - Lote 001',
                    'formula_nombre': 'Pollo Engorde Inicial',
                    'cantidad_programada': 500,
                    'cantidad_producida': 0,
                    'fecha_programada': (datetime.now() + timedelta(hours=2)).strftime('%Y-%m-%d %H:%M'),
                    'fecha_inicio': None,
                    'fecha_completada': None,
                    'estado': 'En Proceso',
                    'prioridad': 'Alta',
                    'observaciones': 'Bachada prioritaria para cliente especial',
                    'tiempo_estimado': 4.5,
                    'tiempo_real': None,
                    'eficiencia': None,
                    'costo_estimado': 625.00,
                    'costo_real': None
                },
                {
                    'id': 2,
                    'codigo': 'BCH-002',
                    'nombre': 'Cerdo Crecimiento - Lote 002',
                    'formula_nombre': 'Cerdo Crecimiento Premium',
                    'cantidad_programada': 750,
                    'cantidad_producida': 0,
                    'fecha_programada': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M'),
                    'fecha_inicio': None,
                    'fecha_completada': None,
                    'estado': 'Programada',
                    'prioridad': 'Normal',
                    'observaciones': 'Cliente especial',
                    'tiempo_estimado': 5.2,
                    'tiempo_real': None,
                    'eficiencia': None,
                    'costo_estimado': 1087.50,
                    'costo_real': None
                },
                {
                    'id': 3,
                    'codigo': 'BCH-003',
                    'nombre': 'Gallina Postura - Lote 003',
                    'formula_nombre': 'Gallina Postura Comercial',
                    'cantidad_programada': 300,
                    'cantidad_producida': 0,
                    'fecha_programada': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d %H:%M'),
                    'fecha_inicio': None,
                    'fecha_completada': None,
                    'estado': 'Programada',
                    'prioridad': 'Normal',
                    'observaciones': '',
                    'tiempo_estimado': 3.8,
                    'tiempo_real': None,
                    'eficiencia': None,
                    'costo_estimado': 405.00,
                    'costo_real': None
                }
            ]
        
        return jsonify({
            'success': True,
            'bachadas': bachadas,
            'total': len(bachadas)
        })
        
    except Exception as e:
        print(f"❌ Error al obtener bachadas: {e}")
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
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Obtener alertas activas de inventario
        cursor.execute("""
            SELECT 
                a.id,
                i.nombre as ingrediente,
                ii.stock_actual,
                ii.stock_minimo,
                ii.unidad,
                a.tipo_alerta,
                a.nivel_prioridad,
                a.mensaje,
                DATE_FORMAT(a.fecha_alerta, '%Y-%m-%d %H:%i') as fecha_alerta,
                a.estado,
                CASE 
                    WHEN a.nivel_prioridad = 'Critica' THEN 'danger'
                    WHEN a.nivel_prioridad = 'Alta' THEN 'warning'
                    WHEN a.nivel_prioridad = 'Media' THEN 'info'
                    ELSE 'secondary'
                END as tipo_bootstrap
            FROM alertas_inventario a
            JOIN inventario_ingredientes ii ON a.inventario_id = ii.id
            JOIN ingredientes i ON ii.ingrediente_id = i.id
            WHERE a.estado = 'Activa' 
            AND ii.usuario_id = %s
            ORDER BY 
                FIELD(a.nivel_prioridad, 'Critica', 'Alta', 'Media', 'Baja'),
                a.fecha_alerta DESC
            LIMIT 10
        """, (session['user_id'],))
        
        alertas = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Si no hay alertas reales, usar datos de ejemplo
        if not alertas:
            alertas = [
                {
                    'id': 1,
                    'ingrediente': 'Maíz Amarillo',
                    'stock_actual': 150,
                    'stock_minimo': 200,
                    'unidad': 'kg',
                    'tipo_alerta': 'Stock Bajo',
                    'nivel_prioridad': 'Alta',
                    'mensaje': 'ALERTA: Maíz Amarillo tiene stock bajo (150 kg restantes)',
                    'fecha_alerta': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'estado': 'Activa',
                    'tipo_bootstrap': 'warning'
                },
                {
                    'id': 2,
                    'ingrediente': 'Harina de Pescado',
                    'stock_actual': 0,
                    'stock_minimo': 100,
                    'unidad': 'kg',
                    'tipo_alerta': 'Agotado',
                    'nivel_prioridad': 'Critica',
                    'mensaje': 'URGENTE: Harina de Pescado está agotado. Reposición inmediata requerida.',
                    'fecha_alerta': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'estado': 'Activa',
                    'tipo_bootstrap': 'danger'
                },
                {
                    'id': 3,
                    'ingrediente': 'Soya Integral',
                    'stock_actual': 500,
                    'stock_minimo': 300,
                    'unidad': 'kg',
                    'tipo_alerta': 'Reposicion Programada',
                    'nivel_prioridad': 'Media',
                    'mensaje': 'INFO: Programar reposición de Soya Integral',
                    'fecha_alerta': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'estado': 'Activa',
                    'tipo_bootstrap': 'info'
                }
            ]
        
        return jsonify({
            'success': True,
            'alertas': alertas,
            'total_alertas': len(alertas)
        })
        
    except Exception as e:
        print(f"❌ Error al obtener alertas de inventario: {e}")
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
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Obtener estadísticas de bachadas
        cursor.execute("""
            SELECT 
                COUNT(*) as total_bachadas,
                SUM(CASE WHEN estado IN ('En Proceso', 'Programada') THEN 1 ELSE 0 END) as bachadas_activas,
                SUM(CASE WHEN estado = 'Completada' THEN 1 ELSE 0 END) as bachadas_completadas,
                SUM(CASE WHEN fecha_programada >= DATE_SUB(NOW(), INTERVAL 7 DAY) 
                         AND estado = 'Completada' THEN cantidad_producida ELSE 0 END) as produccion_semanal,
                AVG(CASE WHEN eficiencia IS NOT NULL THEN eficiencia ELSE NULL END) as eficiencia_promedio,
                AVG(CASE WHEN tiempo_real IS NOT NULL THEN tiempo_real ELSE NULL END) as tiempo_promedio
            FROM bachadas 
            WHERE usuario_id = %s
        """, (session['user_id'],))
        
        stats_bachadas = cursor.fetchone()
        
        # Obtener estadísticas de inventario
        cursor.execute("""
            SELECT 
                SUM(stock_actual) as inventario_total,
                COUNT(*) as total_ingredientes,
                SUM(CASE WHEN estado = 'Bajo Stock' OR stock_actual <= stock_minimo THEN 1 ELSE 0 END) as ingredientes_bajo_stock
            FROM inventario_ingredientes ii
            JOIN ingredientes i ON ii.ingrediente_id = i.id
            WHERE i.usuario_id = %s
        """, (session['user_id'],))
        
        stats_inventario = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        # Calcular estadísticas finales con manejo seguro de None
        try:
            bachadas_activas = int(stats_bachadas['bachadas_activas'] or 0) if stats_bachadas else 0
            inventario_total = float(stats_inventario['inventario_total'] or 0) if stats_inventario else 0
            tiempo_promedio = float(stats_bachadas['tiempo_promedio'] or 4.2) if stats_bachadas else 4.2
            eficiencia_general = float(stats_bachadas['eficiencia_promedio'] or 94.5) if stats_bachadas else 94.5
            produccion_semanal = float(stats_bachadas['produccion_semanal'] or 0) if stats_bachadas else 0
            bachadas_completadas = int(stats_bachadas['bachadas_completadas'] or 0) if stats_bachadas else 0
            ingredientes_bajo_stock = int(stats_inventario['ingredientes_bajo_stock'] or 0) if stats_inventario else 0
        except (TypeError, ValueError, KeyError):
            # Si hay error en conversión, usar valores por defecto
            bachadas_activas = 0
            inventario_total = 0
            tiempo_promedio = 4.2
            eficiencia_general = 94.5
            produccion_semanal = 0
            bachadas_completadas = 0
            ingredientes_bajo_stock = 0
        
        # Meta semanal estimada (basada en capacidad)
        meta_semanal = 16000  # Meta fija por ahora
        porcentaje_meta = (produccion_semanal / meta_semanal * 100) if meta_semanal > 0 else 0
        
        # Si no hay datos reales, usar valores de ejemplo
        if bachadas_activas == 0 and inventario_total == 0:
            estadisticas = {
                'bachadas_activas': 3,
                'inventario_total': 2450,
                'tiempo_promedio': 4.2,
                'eficiencia_general': 94.5,
                'produccion_semanal': 15750,
                'meta_semanal': 16000,
                'porcentaje_meta': 98.4,
                'bachadas_completadas': 12,
                'ingredientes_bajo_stock': 2
            }
        else:
            estadisticas = {
                'bachadas_activas': bachadas_activas,
                'inventario_total': round(inventario_total, 2),
                'tiempo_promedio': round(tiempo_promedio, 1),
                'eficiencia_general': round(eficiencia_general, 1),
                'produccion_semanal': round(produccion_semanal, 2),
                'meta_semanal': meta_semanal,
                'porcentaje_meta': round(porcentaje_meta, 1),
                'bachadas_completadas': bachadas_completadas,
                'ingredientes_bajo_stock': ingredientes_bajo_stock
            }
        
        return jsonify({
            'success': True,
            'estadisticas': estadisticas
        })
        
    except Exception as e:
        print(f"❌ Error al obtener estadísticas de producción: {e}")
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
