from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.db import get_db_connection
from datetime import datetime
import json

reportes_bp = Blueprint('reportes_bp', __name__)

@reportes_bp.route('/reportes')
def reportes():
    """Página principal del generador de reportes"""
    if 'user_id' not in session:
        flash('Debes iniciar sesión para acceder a los reportes.', 'error')
        return redirect(url_for('auth_bp.login'))
    
    return render_template('operaciones/reportes.html')

@reportes_bp.route('/api/mezclas_usuario')
def api_mezclas_usuario():
    """API para obtener las mezclas del usuario actual"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, nombre, tipo_animales, etapa_produccion, 
                   DATE_FORMAT(fecha_creacion, '%d/%m/%Y') as fecha_creacion
            FROM mezclas 
            WHERE usuario_id = %s 
            ORDER BY fecha_creacion DESC
        """, (session['user_id'],))
        
        mezclas = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(mezclas)
        
    except Exception as e:
        print(f"❌ Error al obtener mezclas: {e}")
        return jsonify({'error': 'Error al cargar las mezclas'}), 500

@reportes_bp.route('/api/generar_reporte_comparativo', methods=['POST'])
def generar_reporte_comparativo():
    """Genera un reporte comparativo en PDF entre dos fórmulas"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        data = request.get_json()
        formula_a_id = data.get('formula_a_id')
        formula_b_id = data.get('formula_b_id')
        nombre_cliente = data.get('nombre_cliente', '')
        observaciones = data.get('observaciones', '')
        opciones = data.get('opciones', {})
        
        # Por ahora, simular la generación del reporte
        # En una implementación completa, aquí se generaría el PDF
        
        # Obtener datos básicos de las fórmulas
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT m.*, u.nombre as usuario_nombre, u.moneda, u.unidad_medida
            FROM mezclas m
            JOIN usuarios u ON m.usuario_id = u.id
            WHERE m.id IN (%s, %s) AND m.usuario_id = %s
        """, (formula_a_id, formula_b_id, session['user_id']))
        
        mezclas = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if len(mezclas) != 2:
            return jsonify({'error': 'No se encontraron las fórmulas seleccionadas'}), 404
        
        # Simular respuesta exitosa
        # En una implementación real, aquí se devolvería el PDF generado
        return jsonify({
            'success': True,
            'mensaje': 'Reporte generado exitosamente (simulado)',
            'formulas': [m['nombre'] for m in mezclas],
            'cliente': nombre_cliente,
            'fecha': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        })
        
    except Exception as e:
        print(f"❌ Error al generar reporte comparativo: {e}")
        return jsonify({'error': f'Error al generar el reporte: {str(e)}'}), 500

def registrar_reporte_generado(usuario_id, tipo_reporte, detalles):
    """Registra un reporte generado en el historial"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Por ahora, solo imprimir el registro
        # En una implementación completa, se guardaría en la base de datos
        print(f"📊 Reporte generado - Usuario: {usuario_id}, Tipo: {tipo_reporte}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"⚠️ Error al registrar reporte: {e}")
