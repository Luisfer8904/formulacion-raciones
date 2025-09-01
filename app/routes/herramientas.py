from flask import Blueprint, render_template, session, redirect, url_for
from functools import wraps

herramientas_bp = Blueprint('herramientas_bp', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth_bp.login'))
        return f(*args, **kwargs)
    return decorated_function

@herramientas_bp.route('/herramientas')
@login_required
def herramientas():
    """Página principal de herramientas"""
    return render_template('operaciones/herramientas.html')
