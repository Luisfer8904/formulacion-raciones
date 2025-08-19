from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.db import get_db_connection
from typing import Any
from datetime import datetime

usuarios_bp = Blueprint('usuarios_bp', __name__)

@usuarios_bp.route('/')
def home():
    return render_template('sitio/index.html')

@usuarios_bp.route('/libros')
def libros():
    return render_template('sitio/libros.html')

@usuarios_bp.route('/nosotros')
def nosotros():
    return render_template('sitio/nosotros.html')

@usuarios_bp.route('/caracteristicas')
def caracteristicas():
    return render_template('sitio/caracteristicas.html')

@usuarios_bp.route('/precios')
def precios():
    return render_template('sitio/precios.html')

@usuarios_bp.route('/formulario_cobro')
def formulario_cobro():
    return render_template('sitio/formulario_cobro.html')

@usuarios_bp.route('/procesar_solicitud', methods=['POST'])
def procesar_solicitud():
    try:
        # Obtener datos del formulario
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip()
        telefono = request.form.get('telefono', '').strip()
        empresa = request.form.get('empresa', '').strip()
        pais = request.form.get('pais', '').strip()
        tipo_solicitud = request.form.get('tipo_solicitud', '').strip()
        plan = request.form.get('plan', '').strip()
        comentarios = request.form.get('comentarios', '').strip()
        
        # Validaciones básicas
        if not nombre or not email or not pais or not tipo_solicitud:
            flash('Por favor completa todos los campos obligatorios.', 'error')
            return redirect(url_for('usuarios_bp.formulario_cobro'))
        
        # Si es suscripción, validar que se haya seleccionado un plan
        if tipo_solicitud == 'suscripcion' and not plan:
            flash('Por favor selecciona un plan de suscripción.', 'error')
            return redirect(url_for('usuarios_bp.formulario_cobro'))
        
        # Preparar información para el correo
        asunto = f"Nueva solicitud de {tipo_solicitud.replace('_', ' ').title()} - FeedPro"
        
        mensaje = f"""
        Nueva solicitud recibida:
        
        INFORMACIÓN PERSONAL:
        - Nombre: {nombre}
        - Email: {email}
        - Teléfono: {telefono if telefono else 'No proporcionado'}
        - Empresa: {empresa if empresa else 'No proporcionado'}
        - País: {pais}
        
        TIPO DE SOLICITUD: {tipo_solicitud.replace('_', ' ').title()}
        """
        
        if tipo_solicitud == 'suscripcion' and plan:
            precio_plan = '$24/mes' if plan == 'personal' else '$76/mes'
            mensaje += f"\nPLAN SELECCIONADO: {plan.title()} ({precio_plan})"
        
        if comentarios:
            mensaje += f"\n\nCOMENTARIOS ADICIONALES:\n{comentarios}"
        
        mensaje += f"\n\nFecha de solicitud: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        
        # Enviar correo electrónico (optimizado para Railway)
        try:
            from config_email_railway import enviar_correo_railway_optimizado
            correo_enviado = enviar_correo_railway_optimizado(asunto, mensaje)
            if not correo_enviado:
                # Fallback al método original
                enviar_correo_solicitud(asunto, mensaje)
        except ImportError:
            # Si no está disponible el módulo optimizado, usar el original
            enviar_correo_solicitud(asunto, mensaje)
        
        print("📧 Solicitud recibida:")
        print(f"Asunto: {asunto}")
        print(f"Mensaje: {mensaje}")
        
        # Mensaje de éxito diferente según el tipo de solicitud
        if tipo_solicitud == 'prueba_gratis':
            flash('¡Solicitud de prueba gratuita enviada exitosamente! Te contactaremos pronto para configurar tu acceso.', 'success')
        else:
            plan_nombre = plan.title() if plan else ''
            flash(f'¡Solicitud de suscripción {plan_nombre} enviada exitosamente! Te contactaremos pronto para procesar tu suscripción.', 'success')
        
        return redirect(url_for('usuarios_bp.formulario_cobro'))
        
    except Exception as e:
        print(f"❌ Error al procesar solicitud: {e}")
        flash('Error al procesar la solicitud. Por favor, inténtalo de nuevo.', 'danger')
        return redirect(url_for('usuarios_bp.formulario_cobro'))

@usuarios_bp.route('/panel')
def panel():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para acceder al panel.', 'error')
        return redirect(url_for('auth_bp.login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Total de formulaciones (mezclas) del usuario
    cursor.execute("SELECT COUNT(*) as total FROM mezclas WHERE usuario_id = %s", (session['user_id'],))
    result_formulaciones: Any = cursor.fetchone()
    total_formulaciones = result_formulaciones['total'] if result_formulaciones else 0

    # Total de ingredientes del usuario
    cursor.execute("SELECT COUNT(*) as total FROM ingredientes WHERE usuario_id = %s", (session['user_id'],))
    result_ingredientes: Any = cursor.fetchone()
    total_ingredientes = result_ingredientes['total'] if result_ingredientes else 0

    # Total de reportes — por ahora puedes dejarlo en cero si no tienes reportes implementados
    total_reportes = 0

    # Obtener historial de actividades del usuario actual (últimas 10)
    # Manejar el caso donde la tabla actividades no existe aún
    actividades = []
    try:
        cursor.execute("""
            SELECT descripcion, DATE_FORMAT(fecha, '%d/%m/%Y %H:%i') as fecha_formateada
            FROM actividades 
            WHERE usuario_id = %s 
            ORDER BY fecha DESC 
            LIMIT 10
        """, (session['user_id'],))
        actividades_result = cursor.fetchall()
        
        # Convertir a lista de diccionarios para el template
        if actividades_result:
            for actividad in actividades_result:
                actividad_typed: Any = actividad
                actividades.append({
                    'descripcion': actividad_typed['descripcion'],
                    'fecha': actividad_typed['fecha_formateada']
                })
    except Exception as e:
        print(f"⚠️ Tabla actividades no existe aún: {e}")
        # Actividades permanece como lista vacía
        actividades = []

    cursor.close()
    conn.close()

    return render_template('operaciones/panel.html',
                           total_formulaciones=total_formulaciones,
                           total_ingredientes=total_ingredientes,
                           total_reportes=total_reportes,
                           actividades=actividades)

@usuarios_bp.route('/panelformulador')
def panelformulador():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para acceder.', 'error')
        return redirect(url_for('auth_bp.login'))
    return redirect(url_for('optimizacion_bp.formulacion_minerales'))

@usuarios_bp.route('/opciones')
def opciones():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para acceder a las opciones.', 'error')
        return redirect(url_for('auth_bp.login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT nombre, email, pais, moneda, tipo_moneda, unidad_medida, idioma, tema
        FROM usuarios
        WHERE id = %s
    """, (session['user_id'],))

    usuario = cursor.fetchone() or {}

    cursor.close()
    conn.close()

    return render_template('operaciones/opciones.html', usuario=usuario)

@usuarios_bp.route('/guardar_opciones', methods=['POST'])
def guardar_opciones():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para guardar opciones.', 'error')
        return redirect(url_for('auth_bp.login'))

    nombre = request.form.get('nombre')
    email = request.form.get('email')
    pais = request.form.get('pais')
    moneda = request.form.get('moneda')
    tipo_moneda = request.form.get('tipo_moneda')
    unidad_medida = request.form.get('unidad_medida')
    idioma = request.form.get('idioma')
    tema = request.form.get('tema')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE usuarios SET 
                nombre = %s,
                email = %s,
                pais = %s,
                moneda = %s,
                tipo_moneda = %s,
                unidad_medida = %s,
                idioma = %s,
                tema = %s
            WHERE id = %s
        """, (nombre, email, pais, moneda, tipo_moneda, unidad_medida, idioma, tema, session['user_id']))

        conn.commit()
        cursor.close()
        conn.close()

        flash('Configuración guardada correctamente.', 'success')
        return redirect(url_for('usuarios_bp.opciones'))
    except Exception as e:
        print("❌ Error al guardar opciones:", e)
        flash('Error al guardar la configuración.', 'danger')
        return redirect(url_for('usuarios_bp.opciones'))

@usuarios_bp.route('/hoja_impresion', methods=['POST'])
def hoja_impresion():
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        # Obtener configuración del usuario
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT unidad_medida, moneda, tipo_moneda
            FROM usuarios
            WHERE id = %s
        """, (session['user_id'],))
        config_usuario = cursor.fetchone()
        
        # Si no hay configuración, usar valores por defecto
        if not config_usuario:
            config_usuario = {
                'unidad_medida': 'kg',
                'moneda': 'USD',
                'tipo_moneda': '$'
            }
        
        cursor.close()
        conn.close()
        
        # Recibir datos JSON
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No se recibieron datos'}), 400
        
        # Información básica
        nombre_mezcla = data.get('nombre_mezcla', 'Sin nombre')
        tipo_animales = data.get('tipo_animales', 'No especificado')
        etapa_produccion = data.get('etapa_produccion', 'No especificado')
        observaciones = data.get('observaciones', 'Sin observaciones')
        tamano_bachada = data.get('tamano_bachada', 100)
        total_costo = data.get('total_costo', '0.00')
        suma_inclusion = data.get('suma_inclusion', '0')
        
        # Ingredientes
        ingredientes = data.get('ingredientes', [])
        
        # Nutrientes
        nutrientes = data.get('nutrientes', [])
        
        # Fecha actual
        fecha_actual = datetime.now().strftime('%d de %B de %Y')
        
        return render_template('operaciones/hoja_impresion.html',
                             nombre_mezcla=nombre_mezcla,
                             tipo_animales=tipo_animales,
                             etapa_produccion=etapa_produccion,
                             observaciones=observaciones,
                             tamano_bachada=tamano_bachada,
                             total_costo=total_costo,
                             suma_inclusion=suma_inclusion,
                             total_ingredientes=len(ingredientes),
                             total_nutrientes=len(nutrientes),
                             ingredientes=ingredientes,
                             nutrientes=nutrientes,
                             fecha_actual=fecha_actual,
                             config_usuario=config_usuario)
    
    except Exception as e:
        print("❌ Error en hoja_impresion:", e)
        return jsonify({'error': 'Error interno del servidor'}), 500

def registrar_actividad(usuario_id: int, descripcion: str, tipo_actividad: str = 'general'):
    """
    Función helper para registrar actividades del usuario
    Maneja el caso donde la tabla actividades no existe aún
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO actividades (usuario_id, descripcion, tipo_actividad)
            VALUES (%s, %s, %s)
        """, (usuario_id, descripcion, tipo_actividad))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ Actividad registrada: {descripcion}")
        
    except Exception as e:
        # Si la tabla no existe, solo mostrar un mensaje informativo
        if "doesn't exist" in str(e) or "Table" in str(e):
            print(f"⚠️ Tabla actividades no existe aún - Actividad no registrada: {descripcion}")
        else:
            print(f"❌ Error al registrar actividad: {e}")

def enviar_correo_solicitud(asunto, mensaje):
    """Envía un correo electrónico con la información de la solicitud usando credenciales por variables de entorno.
Optimizado para Railway con múltiples proveedores SMTP y manejo robusto de errores.
Requiere:
- SENDER_EMAIL: cuenta de correo que enviará el correo
- SENDER_PASSWORD: contraseña de aplicación o contraseña del correo
- RECIPIENT_EMAIL: destinatario (si no se define, se envía a la misma SENDER_EMAIL)
"""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    import os
    import socket

    try:
        sender_email = os.getenv('SENDER_EMAIL')
        sender_password = os.getenv('SENDER_PASSWORD')
        recipient_email = os.getenv('RECIPIENT_EMAIL') or sender_email

        # Normalizar: quitar espacios por si se pegó la contraseña de app con espacios
        if sender_password:
            sender_password = sender_password.replace(' ', '')

        # Validaciones previas
        missing = []
        if not sender_email:
            missing.append('SENDER_EMAIL')
        if not sender_password:
            missing.append('SENDER_PASSWORD')

        if missing:
            print(f"❌ Faltan variables de entorno: {', '.join(missing)}")
            return

        # Type assertions para satisfacer Pylance
        sender_email = str(sender_email)
        sender_password = str(sender_password)
        recipient_email = str(recipient_email or sender_email)

        # Configuraciones SMTP múltiples para Railway
        smtp_configs = [
            # Gmail (principal)
            {
                'server': 'smtp.gmail.com',
                'port': 587,
                'use_tls': True,
                'name': 'Gmail'
            },
            # Gmail SSL alternativo
            {
                'server': 'smtp.gmail.com',
                'port': 465,
                'use_tls': False,
                'use_ssl': True,
                'name': 'Gmail SSL'
            },
            # Outlook/Hotmail
            {
                'server': 'smtp-mail.outlook.com',
                'port': 587,
                'use_tls': True,
                'name': 'Outlook'
            },
            # Yahoo
            {
                'server': 'smtp.mail.yahoo.com',
                'port': 587,
                'use_tls': True,
                'name': 'Yahoo'
            }
        ]

        # Detectar proveedor basado en el email
        domain = sender_email.split('@')[1].lower()
        if 'gmail' in domain:
            smtp_configs = [c for c in smtp_configs if 'Gmail' in c['name']] + smtp_configs
        elif 'outlook' in domain or 'hotmail' in domain:
            smtp_configs = [c for c in smtp_configs if 'Outlook' in c['name']] + smtp_configs
        elif 'yahoo' in domain:
            smtp_configs = [c for c in smtp_configs if 'Yahoo' in c['name']] + smtp_configs

        print("📧 Configuración de correo:")
        print(f"   Remitente: {sender_email}")
        print(f"   Destinatario: {recipient_email}")
        print(f"   Contraseña configurada: {'Sí' if sender_password else 'No'}")

        # Crear mensaje
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = asunto
        message.attach(MIMEText(mensaje, "plain", "utf-8"))

        # Intentar con cada configuración SMTP
        for config in smtp_configs:
            try:
                print(f"🔄 Intentando con {config['name']} ({config['server']}:{config['port']})...")
                
                # Configurar timeout más largo para Railway
                socket.setdefaulttimeout(30)
                
                if config.get('use_ssl', False):
                    # Usar SSL directo
                    server = smtplib.SMTP_SSL(config['server'], config['port'], timeout=30)
                else:
                    # Usar conexión normal con TLS
                    server = smtplib.SMTP(config['server'], config['port'], timeout=30)
                    server.ehlo()
                    if config.get('use_tls', True):
                        server.starttls()
                        server.ehlo()

                print("🔄 Autenticando...")
                server.login(sender_email, sender_password)
                
                print("🔄 Enviando correo...")
                server.sendmail(sender_email, [recipient_email], message.as_string())
                server.quit()

                print(f"✅ Correo enviado exitosamente a {recipient_email} usando {config['name']}")
                return  # Éxito, salir de la función

            except smtplib.SMTPAuthenticationError as e:
                print(f"❌ Error de autenticación con {config['name']}: {e}")
                continue
            except smtplib.SMTPConnectError as e:
                print(f"❌ Error de conexión con {config['name']}: {e}")
                continue
            except smtplib.SMTPServerDisconnected as e:
                print(f"❌ Servidor desconectado {config['name']}: {e}")
                continue
            except socket.timeout as e:
                print(f"❌ Timeout con {config['name']}: {e}")
                continue
            except Exception as e:
                print(f"❌ Error con {config['name']}: {e}")
                continue
            finally:
                try:
                    if 'server' in locals():
                        server.quit()
                except:
                    pass

        # Si llegamos aquí, todos los intentos fallaron
        print("❌ No se pudo enviar el correo con ningún proveedor SMTP")
        print("💡 Sugerencias para Railway:")
        print("   1) Verifica que las variables de entorno estén configuradas en Railway")
        print("   2) Usa una contraseña de aplicación para Gmail (no la contraseña normal)")
        print("   3) Verifica que Railway permita conexiones SMTP salientes")
        print("   4) Considera usar un servicio de email como SendGrid o Mailgun")

    except Exception as e:
        print(f"❌ Error general al enviar correo: {e}")
        print("💡 Revisa la configuración de variables de entorno en Railway")
