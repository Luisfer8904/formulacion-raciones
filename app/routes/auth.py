from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.db import get_db_connection
from typing import Any

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form.get('correo')
        contrasena = request.form.get('contrasena')

        # Usuarios hardcodeados para testing (temporal)
        usuarios_test = {
            'admin@formulacion.com': {
                'id': 1,
                'nombre': 'Administrador',
                'email': 'admin@formulacion.com',
                'password': 'admin123',
                'rol': 'admin',
                'tipo_plan': 'profesional'
            },
            'profesional@test.com': {
                'id': 2,
                'nombre': 'Usuario Profesional',
                'email': 'profesional@test.com',
                'password': 'test123',
                'rol': 'user',
                'tipo_plan': 'profesional'
            },
            'personal@test.com': {
                'id': 3,
                'nombre': 'Usuario Personal',
                'email': 'personal@test.com',
                'password': 'test123',
                'rol': 'user',
                'tipo_plan': 'personal'
            },
            'basico@test.com': {
                'id': 4,
                'nombre': 'Usuario Básico',
                'email': 'basico@test.com',
                'password': 'test123',
                'rol': 'user',
                'tipo_plan': 'basico'
            }
        }

        user = None
        
        # Intentar primero con usuarios de testing
        if correo in usuarios_test and usuarios_test[correo]['password'] == contrasena:
            user = usuarios_test[correo]
        else:
            # Intentar con base de datos si está disponible
            try:
                conn = get_db_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM usuarios WHERE email = %s", (correo,))
                user = cursor.fetchone()
                cursor.close()
                conn.close()
                
                # Verificar contraseña de BD
                if user and user.get('password') != contrasena:
                    user = None
                    
            except Exception as e:
                print(f"⚠️ Error de BD (usando usuarios de testing): {e}")
                user = None

        if user is None:
            flash('Usuario no encontrado o contraseña incorrecta.', 'error')
        elif user['rol'] not in ['admin', 'user']:
            flash('No tienes permisos para acceder a esta sección.', 'error')
        else:
            session['user_id'] = user['id']
            session['rol'] = user['rol']
            session['nombre'] = user['nombre']
            session['email'] = user['email']
            
            # Asignar tipo de plan
            if user['rol'] == 'admin':
                session['tipo_plan'] = 'profesional'
            elif user.get('tipo_plan'):
                session['tipo_plan'] = user['tipo_plan']
            else:
                session['tipo_plan'] = 'basico'  # Por defecto: solo herramientas
            
            flash('Inicio de sesión exitoso.', 'success')
            return redirect(url_for('usuarios_bp.panel'))

    return render_template('sitio/login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Has cerrado sesión.', 'success')
    return redirect(url_for('usuarios_bp.home'))
