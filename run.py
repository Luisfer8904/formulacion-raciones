from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    # Configuración para desarrollo
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    port = int(os.environ.get('PORT', 5001))
    host = os.environ.get('HOST', '127.0.0.1')
    
    print(f"🚀 Iniciando aplicación en http://{host}:{port}")
    print(f"🔧 Modo debug: {'Activado' if debug_mode else 'Desactivado'}")
    
    app.run(
        debug=debug_mode,
        host=host,
        port=port,
        threaded=True
    )
