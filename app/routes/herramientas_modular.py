from flask import Blueprint, render_template, session, redirect, url_for
from functools import wraps

# Importar todos los módulos de herramientas
try:
    from .herramientas.conversor_unidades import conversor_unidades_bp
    from .herramientas.calculadora_nutrientes import calculadora_nutrientes_bp
    from .herramientas.gestion_limites import gestion_limites_bp
    from .herramientas.calculadora_aportes import calculadora_aportes_bp
except ImportError as e:
    print(f"⚠️ Error importando herramientas modulares: {e}")
    # Crear blueprints vacíos como fallback
    from flask import Blueprint
    conversor_unidades_bp = Blueprint('conversor_unidades_fallback', __name__)
    calculadora_nutrientes_bp = Blueprint('calculadora_nutrientes_fallback', __name__)
    gestion_limites_bp = Blueprint('gestion_limites_fallback', __name__)
    calculadora_aportes_bp = Blueprint('calculadora_aportes_fallback', __name__)

herramientas_modular_bp = Blueprint('herramientas_modular_bp', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth_bp.login'))
        return f(*args, **kwargs)
    return decorated_function

@herramientas_modular_bp.route('/herramientas_modular')
@login_required
def herramientas():
    """Página principal de herramientas modular"""
    return render_template('operaciones/herramientas_modular.html')

# Función para registrar todos los blueprints de herramientas
def registrar_herramientas_blueprints(app):
    """Registra todos los blueprints de herramientas en la aplicación"""
    app.register_blueprint(conversor_unidades_bp)
    app.register_blueprint(calculadora_nutrientes_bp)
    app.register_blueprint(gestion_limites_bp)
    app.register_blueprint(calculadora_aportes_bp)
    app.register_blueprint(herramientas_modular_bp)
    
    print("✅ Herramientas modulares registradas:")
    print("   - Conversor de Unidades")
    print("   - Calculadora de Nutrientes")
    print("   - Gestión de Límites")
    print("   - Calculadora de Aportes")
