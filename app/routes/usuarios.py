from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.db import get_db_connection
from typing import Any

usuarios_bp = Blueprint('usuarios_bp', __name__)

@usuarios_bp.route('/')
def home():
    return render_template('sitio/index.html')

@usuarios_bp.route('/libros')
def libros():
    return render_template('sitio/libros.html')

@usuarios_bp.route('/nosotros')
def nosotros():
    return render_template('sitio/nosotros.html')

@usuarios_bp.route('/panel')
def panel():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para acceder al panel.', 'error')
        return redirect(url_for('auth_bp.login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Total de formulaciones (mezclas) del usuario
    cursor.execute("SELECT COUNT(*) FROM mezclas WHERE usuario_id = %s", (session['user_id'],))
    result_formulaciones: Any = cursor.fetchone()
    total_formulaciones = result_formulaciones[0] if result_formulaciones else 0

    # Total de ingredientes del usuario
    cursor.execute("SELECT COUNT(*) FROM ingredientes WHERE usuario_id = %s", (session['user_id'],))
    result_ingredientes: Any = cursor.fetchone()
    total_ingredientes = result_ingredientes[0] if result_ingredientes else 0

    # Total de reportes — por ahora puedes dejarlo en cero si no tienes reportes implementados
    total_reportes = 0

    # Historial de actividades vacío por el momento
    actividades = []

    cursor.close()
    conn.close()

    return render_template('operaciones/panel.html',
                           total_formulaciones=total_formulaciones,
                           total_ingredientes=total_ingredientes,
                           total_reportes=total_reportes,
                           actividades=actividades)

@usuarios_bp.route('/panelformulador')
def panelformulador():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para acceder.', 'error')
        return redirect(url_for('auth_bp.login'))
    return redirect(url_for('optimizacion_bp.formulacion_minerales'))

@usuarios_bp.route('/opciones')
def opciones():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para acceder a las opciones.', 'error')
        return redirect(url_for('auth_bp.login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT nombre, email, pais, moneda, tipo_moneda, unidad_medida, idioma, tema
        FROM usuarios
        WHERE id = %s
    """, (session['user_id'],))

    usuario = cursor.fetchone() or {}

    cursor.close()
    conn.close()

    return render_template('operaciones/opciones.html', usuario=usuario)

@usuarios_bp.route('/guardar_opciones', methods=['POST'])
def guardar_opciones():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para guardar opciones.', 'error')
        return redirect(url_for('auth_bp.login'))

    nombre = request.form.get('nombre')
    email = request.form.get('email')
    pais = request.form.get('pais')
    moneda = request.form.get('moneda')
    tipo_moneda = request.form.get('tipo_moneda')
    unidad_medida = request.form.get('unidad_medida')
    idioma = request.form.get('idioma')
    tema = request.form.get('tema')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE usuarios SET 
                nombre = %s,
                email = %s,
                pais = %s,
                moneda = %s,
                tipo_moneda = %s,
                unidad_medida = %s,
                idioma = %s,
                tema = %s
            WHERE id = %s
        """, (nombre, email, pais, moneda, tipo_moneda, unidad_medida, idioma, tema, session['user_id']))

        conn.commit()
        cursor.close()
        conn.close()

        flash('Configuración guardada correctamente.', 'success')
        return redirect(url_for('usuarios_bp.opciones'))
    except Exception as e:
        print("❌ Error al guardar opciones:", e)
        flash('Error al guardar la configuración.', 'danger')
        return redirect(url_for('usuarios_bp.opciones'))
