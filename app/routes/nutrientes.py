from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.db import get_db_connection
from typing import Any

nutrientes_bp = Blueprint('nutrientes_bp', __name__)

@nutrientes_bp.route('/nutrientes')
def ver_nutrientes():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para acceder.', 'error')
        return redirect(url_for('auth_bp.login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, nombre, unidad, tipo FROM nutrientes WHERE usuario_id = %s", (session['user_id'],))
    nutrientes = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('operaciones/ver_nutrientes.html', nutrientes=nutrientes)

@nutrientes_bp.route('/nuevo_nutriente')
def nuevo_nutriente():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para acceder.', 'error')
        return redirect(url_for('auth_bp.login'))
    
    return render_template('operaciones/nuevo_nutriente.html')

@nutrientes_bp.route('/guardar_nutriente', methods=['POST'])
def guardar_nutriente():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para guardar nutrientes.', 'error')
        return redirect(url_for('auth_bp.login'))

    nombre = request.form.get('nombre')
    unidad = request.form.get('unidad')
    tipo = request.form.get('tipo')

    if not nombre or not unidad or not tipo:
        flash('Todos los campos son obligatorios.', 'danger')
        return redirect(url_for('nutrientes_bp.nuevo_nutriente'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO nutrientes (nombre, unidad, tipo, usuario_id) VALUES (%s, %s, %s, %s)", (nombre, unidad, tipo, session['user_id']))
        conn.commit()
        cursor.close()
        conn.close()

        flash('Nutriente guardado correctamente.', 'success')
        return redirect(url_for('nutrientes_bp.ver_nutrientes'))
    except Exception as e:
        print("❌ Error al guardar nutriente:", e)
        flash('Ocurrió un error al guardar el nutriente.', 'danger')
        return redirect(url_for('nutrientes_bp.nuevo_nutriente'))

@nutrientes_bp.route('/editar_nutriente/<int:id>', methods=['GET', 'POST'])
def editar_nutriente(id):
    if 'user_id' not in session:
        flash('Debes iniciar sesión para continuar.', 'error')
        return redirect(url_for('auth_bp.login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        unidad = request.form.get('unidad')
        tipo = request.form.get('tipo')
        cursor.execute("UPDATE nutrientes SET nombre=%s, unidad=%s, tipo=%s WHERE id=%s AND usuario_id=%s", (nombre, unidad, tipo, id, session['user_id']))
        if cursor.rowcount == 0:
            flash('No tienes permisos para editar este nutriente.', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('nutrientes_bp.ver_nutrientes'))
        conn.commit()
        flash('Nutriente actualizado correctamente.', 'success')
        cursor.close()
        conn.close()
        return redirect(url_for('nutrientes_bp.ver_nutrientes'))

    cursor.execute("SELECT * FROM nutrientes WHERE id = %s AND usuario_id = %s", (id, session['user_id']))
    nutriente: Any = cursor.fetchone()
    if not nutriente:
        flash('Nutriente no encontrado o sin permisos.', 'error')
        cursor.close()
        conn.close()
        return redirect(url_for('nutrientes_bp.ver_nutrientes'))
    cursor.close()
    conn.close()

    return render_template('operaciones/editar_nutriente.html', nutriente=nutriente)

@nutrientes_bp.route('/eliminar_nutriente/<int:id>')
def eliminar_nutriente(id):
    if 'user_id' not in session:
        flash('Debes iniciar sesión para continuar.', 'error')
        return redirect(url_for('auth_bp.login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM nutrientes WHERE id = %s AND usuario_id = %s", (id, session['user_id']))
    if cursor.rowcount == 0:
        flash('No tienes permisos para eliminar este nutriente.', 'error')
        cursor.close()
        conn.close()
        return redirect(url_for('nutrientes_bp.ver_nutrientes'))
    conn.commit()
    cursor.close()
    conn.close()

    flash('Nutriente eliminado correctamente.', 'success')
    return redirect(url_for('nutrientes_bp.ver_nutrientes'))
