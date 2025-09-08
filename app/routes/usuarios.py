from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.db import get_db_connection
from typing import Any
from datetime import datetime
import os
import time

usuarios_bp = Blueprint('usuarios_bp', __name__)

@usuarios_bp.route('/health')
def health_check():
    """
    Endpoint de health check para monitorear la salud de la aplicación en Railway
    """
    try:
        # Verificar conexión a base de datos
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        conn.close()
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    # Información del sistema
    health_info = {
        "status": "healthy" if db_status == "ok" else "unhealthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": time.time(),
        "database": db_status,
        "environment": {
            "port": os.environ.get('PORT', 'not_set'),
            "email_configured": bool(os.environ.get('SENDER_EMAIL')),
            "sendgrid_configured": bool(os.environ.get('SENDGRID_API_KEY')),
        },
        "version": "1.0.0"
    }
    
    status_code = 200 if db_status == "ok" else 503
    return jsonify(health_info), status_code

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
    # Obtener el plan desde los parámetros de la URL
    plan_seleccionado = request.args.get('plan', '')
    return render_template('sitio/formulario_cobro.html', plan_seleccionado=plan_seleccionado)

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
        if tipo_solicitud == 'demo':
            asunto = "Nueva solicitud de demostración - FeedPro"
        else:
            asunto = f"Nueva solicitud de {tipo_solicitud.replace('_', ' ').title()} - FeedPro"
        
        mensaje = f"""
        Nueva solicitud recibida:
        
        INFORMACIÓN PERSONAL:
        - Nombre: {nombre}
        - Email: {email}
        - Teléfono: {telefono if telefono else 'No proporcionado'}
        - Empresa: {empresa if empresa else 'No proporcionado'}
        - País: {pais if pais != 'No especificado' else 'No proporcionado'}
        
        TIPO DE SOLICITUD: {tipo_solicitud.replace('_', ' ').title()}
        """
        
        if tipo_solicitud == 'suscripcion' and plan:
            # Mapear precios de planes
            precios_planes = {
                'basico': '$12/mes',
                'avanzado': '$24/mes',
                'profesional': '$56/mes',
                'institucional': 'Precio personalizado'
            }
            precio_plan = precios_planes.get(plan, 'No especificado')
            mensaje += f"\nPLAN SELECCIONADO: {plan.title()} ({precio_plan})"
            
            # Información adicional para plan institucional
            if plan == 'institucional':
                mensaje += f"\n\n⚠️ PLAN INSTITUCIONAL - REQUIERE ATENCIÓN ESPECIAL:"
                mensaje += f"\nEste cliente está interesado en el plan institucional con precio personalizado."
                mensaje += f"\nSe recomienda contactar lo antes posible para discutir:"
                mensaje += f"\n- Número de usuarios requeridos"
                mensaje += f"\n- Funcionalidades específicas necesarias"
                mensaje += f"\n- Volumen de operación"
                mensaje += f"\n- Presupuesto disponible"
                mensaje += f"\n- Cronograma de implementación"
        
        if comentarios:
            if tipo_solicitud == 'demo':
                mensaje += f"\n\nCONSULTA SOBRE FEEDPRO:\n{comentarios}"
            else:
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
        if tipo_solicitud == 'demo':
            flash('¡Solicitud de demostración enviada exitosamente! Te contactaremos pronto para agendar tu demo personalizada.', 'success')
            return redirect(url_for('usuarios_bp.home'))
        elif tipo_solicitud == 'prueba_gratis':
            flash('¡Solicitud de prueba gratuita enviada exitosamente! Te contactaremos pronto para configurar tu acceso.', 'success')
            return redirect(url_for('usuarios_bp.formulario_cobro'))
        else:
            plan_nombre = plan.title() if plan else ''
            if plan == 'institucional':
                flash(f'¡Solicitud de plan {plan_nombre} enviada exitosamente! Nuestro equipo de ventas se contactará contigo pronto para discutir los detalles y precios personalizados.', 'success')
            else:
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

    # Total de nutrientes del usuario
    cursor.execute("SELECT COUNT(*) as total FROM nutrientes WHERE usuario_id = %s", (session['user_id'],))
    result_nutrientes: Any = cursor.fetchone()
    total_nutrientes = result_nutrientes['total'] if result_nutrientes else 0

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
                           total_nutrientes=total_nutrientes,
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
        SELECT nombre, email, pais, moneda, unidad_medida, idioma, tema, tipo_plan
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
    # No permitir cambiar el email desde opciones
    pais = request.form.get('pais')
    moneda = request.form.get('moneda')
    unidad_medida = request.form.get('unidad_medida')
    idioma = request.form.get('idioma')
    tema = request.form.get('tema')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE usuarios SET 
                nombre = %s,
                pais = %s,
                moneda = %s,
                unidad_medida = %s,
                idioma = %s,
                tema = %s
            WHERE id = %s
        """, (nombre, pais, moneda, unidad_medida, idioma, tema, session['user_id']))

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
        materia_seca_total = data.get('materia_seca_total', '0.00')
        
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
                             materia_seca_total=materia_seca_total,
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

@usuarios_bp.route('/mejorar_plan', methods=['POST'])
def mejorar_plan():
    """Procesar solicitud de mejora de plan"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401

    try:
        # Obtener datos del usuario
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT nombre, email, tipo_plan
            FROM usuarios
            WHERE id = %s
        """, (session['user_id'],))
        
        usuario_data: Any = cursor.fetchone()
        if not usuario_data:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        # Obtener datos del formulario
        tipo_mejora = request.form.get('tipo_mejora', '').strip()
        mensaje = request.form.get('mensaje', '').strip()
        telefono = request.form.get('telefono', '').strip()
        
        # Validaciones
        if not tipo_mejora or not mensaje:
            return jsonify({'error': 'Todos los campos obligatorios deben ser completados'}), 400

        # Mapear tipos de mejora para el email
        tipos_mejora_map = {
            'upgrade': 'Actualizar a plan superior',
            'funciones': 'Consultar funciones adicionales',
            'precios': 'Información sobre precios',
            'personalizado': 'Plan personalizado',
            'otro': 'Otro'
        }
        
        tipo_mejora_texto = tipos_mejora_map.get(tipo_mejora, tipo_mejora)
        plan_actual = str(usuario_data.get('tipo_plan', 'básico')).title()

        # Preparar email
        asunto = f"Solicitud de mejora de plan - {str(usuario_data['nombre'])} - FeedPro"
        
        mensaje_email = f"""
Nueva solicitud de mejora de plan recibida:

INFORMACIÓN DEL USUARIO:
- Nombre: {str(usuario_data['nombre'])}
- Email: {str(usuario_data['email'])}
- Plan actual: {plan_actual}
- Teléfono: {telefono if telefono else 'No proporcionado'}

SOLICITUD:
- Tipo de consulta: {tipo_mejora_texto}
- Mensaje del usuario:
{mensaje}

Fecha de solicitud: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

---
Este mensaje fue enviado automáticamente desde el panel de usuario de FeedPro.
        """

        # Enviar correo electrónico
        try:
            from config_email_railway import enviar_correo_railway_optimizado
            correo_enviado = enviar_correo_railway_optimizado(asunto, mensaje_email)
            if not correo_enviado:
                # Fallback al método original
                enviar_correo_solicitud(asunto, mensaje_email)
        except ImportError:
            # Si no está disponible el módulo optimizado, usar el original
            enviar_correo_solicitud(asunto, mensaje_email)

        # Registrar actividad
        registrar_actividad(session['user_id'], f'Solicitó mejora de plan: {tipo_mejora_texto}', 'plan')

        cursor.close()
        conn.close()

        print("📧 Solicitud de mejora de plan enviada:")
        print(f"Usuario: {usuario_data['nombre']} ({usuario_data['email']})")
        print(f"Tipo: {tipo_mejora_texto}")
        print(f"Plan actual: {plan_actual}")

        return jsonify({'success': True, 'mensaje': 'Solicitud enviada exitosamente'}), 200

    except Exception as e:
        print(f"❌ Error al procesar solicitud de mejora: {e}")
        return jsonify({'error': 'Error al procesar la solicitud'}), 500

@usuarios_bp.route('/cancelar_plan', methods=['POST'])
def cancelar_plan():
    """Cancelar el plan actual del usuario y volver al plan básico"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401

    try:
        # Obtener datos del usuario
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT nombre, email, tipo_plan
            FROM usuarios
            WHERE id = %s
        """, (session['user_id'],))
        
        usuario_data: Any = cursor.fetchone()
        if not usuario_data:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        # Obtener datos adicionales de la cancelación
        data = request.get_json() or {}
        motivo = data.get('motivo', '').strip()
        comentarios = data.get('comentarios', '').strip()
        telefono = data.get('telefono', '').strip()

        plan_anterior = str(usuario_data.get('tipo_plan', 'básico')).title()

        # Actualizar el plan del usuario a básico
        cursor.execute("""
            UPDATE usuarios 
            SET tipo_plan = 'basico'
            WHERE id = %s
        """, (session['user_id'],))

        conn.commit()

        # Preparar email de notificación de cancelación
        asunto = f"Cancelación de plan - {str(usuario_data['nombre'])} - FeedPro"
        
        mensaje_email = f"""
Un usuario ha solicitado la cancelación de su plan de suscripción:

INFORMACIÓN DEL USUARIO:
- Nombre: {str(usuario_data['nombre'])}
- Email: {str(usuario_data['email'])}
- Teléfono: {telefono if telefono else 'No proporcionado'}
- Plan actual: {plan_anterior}

DETALLES DE LA SOLICITUD:
- Motivo: {motivo if motivo else 'No especificado'}
- Comentarios adicionales: {comentarios if comentarios else 'Ninguno'}

Fecha de solicitud: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

ACCIÓN REQUERIDA:
El usuario solicita cancelar su plan {plan_anterior}. 
Se recomienda contactar al usuario para:
1. Confirmar los detalles de la cancelación
2. Entender mejor sus necesidades 
3. Posiblemente ofrecer alternativas antes de procesar la baja definitiva

---
Este mensaje fue enviado automáticamente desde el sistema de FeedPro.
        """

        # Enviar correo electrónico de notificación
        try:
            from config_email_railway import enviar_correo_railway_optimizado
            correo_enviado = enviar_correo_railway_optimizado(asunto, mensaje_email)
            if not correo_enviado:
                # Fallback al método original
                enviar_correo_solicitud(asunto, mensaje_email)
        except ImportError:
            # Si no está disponible el módulo optimizado, usar el original
            enviar_correo_solicitud(asunto, mensaje_email)

        # Registrar actividad
        motivo_texto = f" (Motivo: {motivo})" if motivo else ""
        registrar_actividad(session['user_id'], f'Canceló su plan de suscripción{motivo_texto}', 'plan')

        cursor.close()
        conn.close()

        print("📧 Cancelación de plan procesada:")
        print(f"Usuario: {usuario_data['nombre']} ({usuario_data['email']})")
        print(f"Plan cancelado: {plan_anterior}")
        print(f"Motivo: {motivo if motivo else 'No especificado'}")

        return jsonify({'success': True, 'mensaje': 'Plan cancelado exitosamente'}), 200

    except Exception as e:
        print(f"❌ Error al cancelar plan: {e}")
        return jsonify({'error': 'Error al cancelar el plan'}), 500

# ==========================================
# RUTAS DE ADMINISTRADOR
# ==========================================

def admin_required(f):
    """Decorador para requerir permisos de administrador"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión para acceder.', 'error')
            return redirect(url_for('auth_bp.login'))
        if session.get('rol') != 'admin':
            flash('No tienes permisos para acceder a esta sección.', 'error')
            return redirect(url_for('usuarios_bp.panel'))
        return f(*args, **kwargs)
    return decorated_function

@usuarios_bp.route('/administrador')
@admin_required
def administrador():
    """Panel de administración de usuarios"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Obtener todos los usuarios
        cursor.execute("""
            SELECT id, nombre, email, rol, tipo_plan, pais, 
                   DATE_FORMAT(fecha_creacion, '%d/%m/%Y') as fecha_creacion_formateada,
                   fecha_creacion
            FROM usuarios 
            ORDER BY fecha_creacion DESC
        """)
        usuarios = cursor.fetchall()
        
        # Estadísticas generales
        cursor.execute("SELECT COUNT(*) as total FROM usuarios")
        result_total: Any = cursor.fetchone()
        total_usuarios = result_total['total'] if result_total else 0
        
        cursor.execute("SELECT COUNT(*) as total FROM usuarios WHERE rol = 'admin'")
        result_admins: Any = cursor.fetchone()
        total_admins = result_admins['total'] if result_admins else 0
        
        cursor.execute("SELECT COUNT(*) as total FROM usuarios WHERE rol = 'user'")
        result_users: Any = cursor.fetchone()
        total_users = result_users['total'] if result_users else 0
        
        cursor.close()
        conn.close()
        
        return render_template('operaciones/administrador.html',
                             usuarios=usuarios,
                             total_usuarios=total_usuarios,
                             total_admins=total_admins,
                             total_users=total_users)
                             
    except Exception as e:
        print(f"❌ Error en administrador: {e}")
        flash('Error al cargar el panel de administración.', 'error')
        return redirect(url_for('usuarios_bp.panel'))

@usuarios_bp.route('/admin/crear_usuario', methods=['POST'])
@admin_required
def crear_usuario():
    """Crear un nuevo usuario"""
    try:
        # Obtener datos del formulario
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        rol = request.form.get('rol', 'user').strip()
        tipo_plan = request.form.get('tipo_plan', 'basico').strip()
        pais = request.form.get('pais', '').strip()
        
        # Validaciones
        if not nombre or not email or not password:
            flash('Todos los campos obligatorios deben ser completados.', 'error')
            return redirect(url_for('usuarios_bp.administrador'))
        
        if rol not in ['admin', 'user']:
            flash('Rol inválido.', 'error')
            return redirect(url_for('usuarios_bp.administrador'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar si el email ya existe
        cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
        if cursor.fetchone():
            flash('Ya existe un usuario con ese correo electrónico.', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('usuarios_bp.administrador'))
        
        # Crear el usuario
        cursor.execute("""
            INSERT INTO usuarios (nombre, email, password, rol, tipo_plan, pais, fecha_creacion)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """, (nombre, email, password, rol, tipo_plan, pais))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Registrar actividad
        registrar_actividad(session['user_id'], f'Creó el usuario: {nombre} ({email})', 'admin')
        
        flash(f'Usuario {nombre} creado exitosamente.', 'success')
        return redirect(url_for('usuarios_bp.administrador'))
        
    except Exception as e:
        print(f"❌ Error al crear usuario: {e}")
        flash('Error al crear el usuario.', 'error')
        return redirect(url_for('usuarios_bp.administrador'))

@usuarios_bp.route('/admin/editar_usuario/<int:usuario_id>', methods=['POST'])
@admin_required
def editar_usuario(usuario_id):
    """Editar un usuario existente"""
    try:
        # Obtener datos del formulario
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip()
        rol = request.form.get('rol', 'user').strip()
        tipo_plan = request.form.get('tipo_plan', 'basico').strip()
        pais = request.form.get('pais', '').strip()
        password = request.form.get('password', '').strip()
        
        # Validaciones
        if not nombre or not email:
            flash('Nombre y email son obligatorios.', 'error')
            return redirect(url_for('usuarios_bp.administrador'))
        
        if rol not in ['admin', 'user']:
            flash('Rol inválido.', 'error')
            return redirect(url_for('usuarios_bp.administrador'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar que el usuario existe
        cursor.execute("SELECT nombre FROM usuarios WHERE id = %s", (usuario_id,))
        usuario_actual = cursor.fetchone()
        if not usuario_actual:
            flash('Usuario no encontrado.', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('usuarios_bp.administrador'))
        
        # Verificar si el email ya existe en otro usuario
        cursor.execute("SELECT id FROM usuarios WHERE email = %s AND id != %s", (email, usuario_id))
        if cursor.fetchone():
            flash('Ya existe otro usuario con ese correo electrónico.', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('usuarios_bp.administrador'))
        
        # Actualizar el usuario
        if password:
            # Si se proporciona nueva contraseña, actualizarla también
            cursor.execute("""
                UPDATE usuarios 
                SET nombre = %s, email = %s, rol = %s, tipo_plan = %s, pais = %s, password = %s
                WHERE id = %s
            """, (nombre, email, rol, tipo_plan, pais, password, usuario_id))
        else:
            # Si no se proporciona contraseña, no actualizarla
            cursor.execute("""
                UPDATE usuarios 
                SET nombre = %s, email = %s, rol = %s, tipo_plan = %s, pais = %s
                WHERE id = %s
            """, (nombre, email, rol, tipo_plan, pais, usuario_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Registrar actividad
        registrar_actividad(session['user_id'], f'Editó el usuario: {nombre} ({email})', 'admin')
        
        flash(f'Usuario {nombre} actualizado exitosamente.', 'success')
        return redirect(url_for('usuarios_bp.administrador'))
        
    except Exception as e:
        print(f"❌ Error al editar usuario: {e}")
        flash('Error al editar el usuario.', 'error')
        return redirect(url_for('usuarios_bp.administrador'))

@usuarios_bp.route('/admin/eliminar_usuario/<int:usuario_id>', methods=['POST'])
@admin_required
def eliminar_usuario(usuario_id):
    """Eliminar un usuario"""
    try:
        # No permitir que el admin se elimine a sí mismo
        if usuario_id == session['user_id']:
            flash('No puedes eliminar tu propia cuenta.', 'error')
            return redirect(url_for('usuarios_bp.administrador'))
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Obtener información del usuario antes de eliminarlo
        cursor.execute("SELECT nombre, email FROM usuarios WHERE id = %s", (usuario_id,))
        usuario: Any = cursor.fetchone()
        
        if not usuario:
            flash('Usuario no encontrado.', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('usuarios_bp.administrador'))
        
        # Eliminar el usuario
        cursor.execute("DELETE FROM usuarios WHERE id = %s", (usuario_id,))
        
        if cursor.rowcount == 0:
            flash('No se pudo eliminar el usuario.', 'error')
        else:
            # Registrar actividad
            registrar_actividad(session['user_id'], f'Eliminó el usuario: {usuario["nombre"]} ({usuario["email"]})', 'admin')
            flash(f'Usuario {usuario["nombre"]} eliminado exitosamente.', 'success')
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return redirect(url_for('usuarios_bp.administrador'))
        
    except Exception as e:
        print(f"❌ Error al eliminar usuario: {e}")
        flash('Error al eliminar el usuario.', 'error')
        return redirect(url_for('usuarios_bp.administrador'))

@usuarios_bp.route('/admin/api/usuarios')
@admin_required
def api_usuarios():
    """API para obtener lista de usuarios (para búsqueda/filtrado)"""
    try:
        search = request.args.get('search', '').strip()
        rol_filter = request.args.get('rol', '').strip()
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Construir query con filtros
        query = """
            SELECT id, nombre, email, rol, tipo_plan, pais,
                   DATE_FORMAT(fecha_creacion, '%d/%m/%Y') as fecha_creacion_formateada
            FROM usuarios 
            WHERE 1=1
        """
        params = []
        
        if search:
            query += " AND (nombre LIKE %s OR email LIKE %s)"
            params.extend([f'%{search}%', f'%{search}%'])
        
        if rol_filter and rol_filter in ['admin', 'user']:
            query += " AND rol = %s"
            params.append(rol_filter)
        
        query += " ORDER BY fecha_creacion DESC"
        
        cursor.execute(query, params)
        usuarios = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({'usuarios': usuarios})
        
    except Exception as e:
        print(f"❌ Error en API usuarios: {e}")
        return jsonify({'error': 'Error al obtener usuarios'}), 500
