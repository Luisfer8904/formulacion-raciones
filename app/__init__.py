from flask import Flask
import re
import os
from .routes.ingredientes import ingredientes_bp
from .routes.requerimientos import requerimientos_bp
from .routes.nutrientes import nutrientes_bp
from .routes.auth import auth_bp
from .routes.mezclas import mezclas_bp
from .routes.optimizacion import optimizacion_bp
from .routes.usuarios import usuarios_bp

def create_app():
    # Configurar las rutas de templates y static desde la raíz del proyecto
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
    
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.secret_key = os.environ.get('SECRET_KEY', 'clave_segura')

    # Filtro personalizado para reemplazo con regex en plantillas Jinja2
    @app.template_filter('regex_replace')
    def regex_replace(s, find, replace):
        return re.sub(find, replace, s)

    # Registrar blueprints
    app.register_blueprint(ingredientes_bp)
    app.register_blueprint(requerimientos_bp)
    app.register_blueprint(nutrientes_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(mezclas_bp)
    app.register_blueprint(optimizacion_bp)
    app.register_blueprint(usuarios_bp)

    return app
