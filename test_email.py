#!/usr/bin/env python3
"""
Script de prueba para verificar el envío de correos
"""

import os
import sys

# Configurar variables de entorno
os.environ['SENDER_EMAIL'] = 'feedpro07@gmail.com'
os.environ['SENDER_PASSWORD'] = 'hfawobjfxrtkaapi'
os.environ['RECIPIENT_EMAIL'] = 'lfrivera8904@gmail.com'

# Agregar el directorio actual al path para importar la app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.routes.usuarios import enviar_correo_solicitud

def test_email():
    """Probar el envío de correo"""
    print("🧪 Probando envío de correo...")
    
    asunto = "Prueba de correo - FeedPro"
    mensaje = """
    Esta es una prueba del sistema de correos de FeedPro.
    
    INFORMACIÓN DE PRUEBA:
    - Nombre: Luis Rivera
    - Email: lfrivera8904@gmail.com
    - País: Colombia
    - Tipo: Prueba Gratis
    
    Si recibes este correo, el sistema está funcionando correctamente.
    """
    
    try:
        enviar_correo_solicitud(asunto, mensaje)
        print("✅ Prueba de correo completada exitosamente")
        return True
    except Exception as e:
        print(f"❌ Error en la prueba de correo: {e}")
        return False

if __name__ == "__main__":
    success = test_email()
    sys.exit(0 if success else 1)
