"""
Configuración de email alternativa para Railway usando SendGrid
SendGrid es más confiable en entornos de contenedores como Railway
"""
import os
import requests
import json
from typing import Optional

def enviar_correo_sendgrid(asunto: str, mensaje: str, destinatario: Optional[str] = None) -> bool:
    """
    Envía correo usando SendGrid API (más confiable en Railway que SMTP)
    """
    try:
        api_key = os.getenv('SENDGRID_API_KEY')
        from_email = os.getenv('SENDGRID_FROM_EMAIL', os.getenv('SENDER_EMAIL'))
        to_email = destinatario or os.getenv('RECIPIENT_EMAIL') or from_email
        
        if not api_key:
            print("❌ SENDGRID_API_KEY no configurado")
            return False
            
        if not from_email:
            print("❌ SENDGRID_FROM_EMAIL no configurado")
            return False
        
        # Datos para SendGrid API
        data = {
            "personalizations": [
                {
                    "to": [{"email": to_email}],
                    "subject": asunto
                }
            ],
            "from": {"email": from_email},
            "content": [
                {
                    "type": "text/plain",
                    "value": mensaje
                }
            ]
        }
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        print(f"📧 Enviando correo via SendGrid API...")
        print(f"   De: {from_email}")
        print(f"   Para: {to_email}")
        
        response = requests.post(
            "https://api.sendgrid.com/v3/mail/send",
            headers=headers,
            data=json.dumps(data),
            timeout=30
        )
        
        if response.status_code == 202:
            print("✅ Correo enviado exitosamente via SendGrid")
            return True
        else:
            print(f"❌ Error SendGrid: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error al enviar correo via SendGrid: {e}")
        return False

def enviar_correo_webhook(asunto: str, mensaje: str, destinatario: Optional[str] = None) -> bool:
    """
    Envía correo usando webhook (alternativa simple para Railway)
    """
    try:
        webhook_url = os.getenv('EMAIL_WEBHOOK_URL')
        
        if not webhook_url:
            print("❌ EMAIL_WEBHOOK_URL no configurado")
            return False
        
        from_email = os.getenv('SENDER_EMAIL', 'noreply@feedpro.com')
        to_email = destinatario or os.getenv('RECIPIENT_EMAIL') or from_email
        
        data = {
            "from": from_email,
            "to": to_email,
            "subject": asunto,
            "message": mensaje,
            "timestamp": str(int(time.time()))
        }
        
        print(f"📧 Enviando correo via Webhook...")
        print(f"   URL: {webhook_url}")
        print(f"   Para: {to_email}")
        
        response = requests.post(
            webhook_url,
            json=data,
            timeout=30,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code in [200, 201, 202]:
            print("✅ Correo enviado exitosamente via Webhook")
            return True
        else:
            print(f"❌ Error Webhook: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error al enviar correo via Webhook: {e}")
        return False

def enviar_correo_railway_optimizado(asunto: str, mensaje: str, destinatario: Optional[str] = None) -> bool:
    """
    Sistema de email optimizado para Railway con múltiples métodos
    """
    print("🚀 Iniciando envío de correo optimizado para Railway...")
    
    # Método 1: SendGrid API (más confiable)
    if enviar_correo_sendgrid(asunto, mensaje, destinatario):
        return True
    
    # Método 2: Webhook personalizado
    if enviar_correo_webhook(asunto, mensaje, destinatario):
        return True
    
    # Método 3: SMTP con configuración específica para Railway
    if enviar_correo_smtp_railway(asunto, mensaje, destinatario):
        return True
    
    # Método 4: Guardar en base de datos como respaldo
    if guardar_correo_pendiente(asunto, mensaje, destinatario):
        print("📝 Correo guardado en base de datos para envío posterior")
        return True
    
    print("❌ No se pudo enviar el correo con ningún método")
    return False

def enviar_correo_smtp_railway(asunto: str, mensaje: str, destinatario: Optional[str] = None) -> bool:
    """
    SMTP específicamente configurado para Railway
    """
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    import socket
    
    try:
        sender_email = os.getenv('SENDER_EMAIL')
        sender_password = os.getenv('SENDER_PASSWORD')
        recipient_email = destinatario or os.getenv('RECIPIENT_EMAIL') or sender_email
        
        if not sender_email or not sender_password:
            return False
        
        # Configuración específica para Railway
        smtp_configs = [
            # Gmail con configuración Railway-optimizada
            {
                'server': 'smtp.gmail.com',
                'port': 587,
                'use_tls': True,
                'name': 'Gmail Railway'
            },
            # Alternativa con puerto 465
            {
                'server': 'smtp.gmail.com', 
                'port': 465,
                'use_ssl': True,
                'name': 'Gmail SSL Railway'
            }
        ]
        
        message = MIMEMultipart()
        message["From"] = str(sender_email)
        message["To"] = str(recipient_email)
        message["Subject"] = asunto
        message.attach(MIMEText(mensaje, "plain", "utf-8"))
        
        for config in smtp_configs:
            try:
                print(f"🔄 Intentando SMTP Railway: {config['name']}")
                
                # Configuración específica para Railway
                socket.setdefaulttimeout(60)  # Timeout más largo
                
                if config.get('use_ssl'):
                    server = smtplib.SMTP_SSL(config['server'], config['port'], timeout=60)
                else:
                    server = smtplib.SMTP(config['server'], config['port'], timeout=60)
                    server.ehlo()
                    server.starttls()
                    server.ehlo()
                
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, [str(recipient_email)], message.as_string())
                server.quit()
                
                print(f"✅ Correo enviado via {config['name']}")
                return True
                
            except Exception as e:
                print(f"❌ Error {config['name']}: {e}")
                continue
        
        return False
        
    except Exception as e:
        print(f"❌ Error SMTP Railway: {e}")
        return False

def guardar_correo_pendiente(asunto: str, mensaje: str, destinatario: Optional[str] = None) -> bool:
    """
    Guarda el correo en base de datos para envío posterior
    """
    try:
        from app.db import get_db_connection
        import json
        from datetime import datetime
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Crear tabla si no existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS correos_pendientes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                asunto VARCHAR(255),
                mensaje TEXT,
                destinatario VARCHAR(255),
                datos_extra JSON,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                enviado BOOLEAN DEFAULT FALSE
            )
        """)
        
        # Insertar correo pendiente
        cursor.execute("""
            INSERT INTO correos_pendientes (asunto, mensaje, destinatario, datos_extra)
            VALUES (%s, %s, %s, %s)
        """, (
            asunto,
            mensaje,
            destinatario or os.getenv('RECIPIENT_EMAIL'),
            json.dumps({
                "timestamp": datetime.now().isoformat(),
                "method": "database_backup",
                "railway_deployment": True
            })
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Correo guardado en base de datos")
        return True
        
    except Exception as e:
        print(f"❌ Error al guardar correo: {e}")
        return False
