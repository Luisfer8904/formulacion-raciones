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
from .routes.reportes_mejorado import reportes_mejorado_bp
from .routes.herramientas import herramientas_bp
from .routes.calculadora_aportes import calculadora_aportes_bp
from .routes.calculadora_nutricional import calculadora_nutricional_bp
from .routes.calculadora_aportes_nueva import calculadora_aportes_nueva_bp
from .routes.planificador import planificador_bp
from .routes.conversor_unidades_avanzado import conversor_avanzado_bp
from .routes.reporte_comparativo import reporte_comparativo_bp
from .routes.calculadora_ingredientes import calculadora_ingredientes_bp

def create_app():
    # Cargar variables de entorno desde archivo .env
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Variables de entorno cargadas desde .env")
    except ImportError:
        print("⚠️ python-dotenv no instalado, usando variables de entorno del sistema")
    
    # Configurar las rutas de templates y static desde la raíz del proyecto
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
    
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.secret_key = os.environ.get('SECRET_KEY', 'clave_segura')
    
    # Verificar configuración de email
    print("📧 Configuración de email:")
    print(f"   SENDER_EMAIL: {os.environ.get('SENDER_EMAIL', 'No configurado')}")
    print(f"   SENDER_PASSWORD: {'Configurado' if os.environ.get('SENDER_PASSWORD') else 'No configurado'}")
    print(f"   RECIPIENT_EMAIL: {os.environ.get('RECIPIENT_EMAIL', 'No configurado')}")

    # Filtro personalizado para reemplazo con regex en plantillas Jinja2
    @app.template_filter('regex_replace')
    def regex_replace(s, find, replace):
        return re.sub(find, replace, s)
    
    # Función para convertir códigos de moneda a símbolos
    def obtener_simbolo_moneda(codigo_moneda):
        """Convierte códigos de moneda a sus símbolos correspondientes"""
        simbolos_moneda = {
            # Centroamérica
            'HNL': 'L',
            'GTQ': 'Q', 
            'USD': '$',
            'CRC': '₡',
            'NIO': 'C$',
            'PAB': 'B/.',
            # Norteamérica
            'MXN': '$',
            'CAD': 'C$',
            # Sudamérica
            'COP': '$',
            'VES': 'Bs.',
            'PEN': 'S/',
            'BOB': 'Bs.',
            'BRL': 'R$',
            'PYG': '₲',
            'UYU': '$U',
            'ARS': '$',
            'CLP': '$',
            # Europa
            'EUR': '€',
            'GBP': '£',
            # Otros
            'DOP': 'RD$',
            'CUP': '$',
            'JPY': '¥'
        }
        return simbolos_moneda.get(codigo_moneda, codigo_moneda)
    
    # Filtro para templates
    @app.template_filter('simbolo_moneda')
    def simbolo_moneda_filter(codigo_moneda):
        return obtener_simbolo_moneda(codigo_moneda)
    
    # Función global disponible en todos los templates
    @app.context_processor
    def utility_processor():
        return dict(obtener_simbolo_moneda=obtener_simbolo_moneda)

    # Registrar blueprints
    app.register_blueprint(ingredientes_bp)
    app.register_blueprint(requerimientos_bp)
    app.register_blueprint(nutrientes_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(mezclas_bp)
    app.register_blueprint(optimizacion_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(reportes_mejorado_bp)
    app.register_blueprint(herramientas_bp)
    app.register_blueprint(calculadora_aportes_bp)
    app.register_blueprint(calculadora_nutricional_bp)
    app.register_blueprint(calculadora_aportes_nueva_bp)
    app.register_blueprint(planificador_bp)
    app.register_blueprint(conversor_avanzado_bp)
    app.register_blueprint(reporte_comparativo_bp)
    app.register_blueprint(calculadora_ingredientes_bp)

    return app
