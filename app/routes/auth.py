from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.db import get_db_connection
from typing import Any

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form.get('correo')
        contrasena = request.form.get('contrasena')

        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios WHERE email = %s", (correo,))
            user: Any = cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

        if user is None:
            flash('Usuario no encontrado.', 'error')
        elif 'password' not in user or user['password'] != contrasena:
            flash('Contraseña incorrecta o no definida.', 'error')
        elif user['rol'] not in ['admin', 'user']:
            flash('No tienes permisos para acceder a esta sección.', 'error')
        else:
            session['user_id'] = user['id']
            session['rol'] = user['rol']
            session['nombre'] = user['nombre']
            session['email'] = user['email']
            flash('Inicio de sesión exitoso.', 'success')
            return redirect(url_for('usuarios_bp.panel'))

    return render_template('sitio/login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Has cerrado sesión.', 'success')
    return redirect(url_for('usuarios_bp.home'))
