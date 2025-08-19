"""
Configuración de correo electrónico para FeedPro
Instrucciones para configurar Gmail:

1. Ve a tu cuenta de Google: https://myaccount.google.com/
2. Seguridad > Verificación en 2 pasos (debe estar activada)
3. Seguridad > Contraseñas de aplicaciones
4. Genera una nueva contraseña de aplicación para "Correo"
5. Usa esa contraseña (no tu contraseña normal) en SENDER_PASSWORD

Alternativa: Configura las variables de entorno en tu sistema:
export SENDER_EMAIL="tu_correo@gmail.com"
export SENDER_PASSWORD="tu_contraseña_de_aplicacion"
export RECIPIENT_EMAIL="donde_quieres_recibir@correo.com"
"""

# Configuración de correo
EMAIL_CONFIG = {
    'SMTP_SERVER': 'smtp.gmail.com',
    'SMTP_PORT': 587,
    'SENDER_EMAIL': 'feedpro07@gmail.com',  # Correo que envía
    'SENDER_PASSWORD': 'Luis82847',  # Contraseña
    'RECIPIENT_EMAIL': 'lfrivera8904@gmail.com'  # Correo donde recibes las solicitudes
}

# Para otros proveedores de correo:
# 
# OUTLOOK/HOTMAIL:
# SMTP_SERVER = 'smtp-mail.outlook.com'
# SMTP_PORT = 587
#
# YAHOO:
# SMTP_SERVER = 'smtp.mail.yahoo.com'
# SMTP_PORT = 587
