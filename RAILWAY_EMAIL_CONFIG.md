# Configuración de Email para Railway

## ⚡ NUEVO: Sistema Optimizado para Railway

El sistema ahora incluye múltiples métodos de envío para garantizar que funcione en Railway:

1. **SendGrid API** (Recomendado para Railway)
2. **Webhook personalizado** 
3. **SMTP optimizado** (con configuración específica para Railway)
4. **Base de datos** (respaldo automático)

## Variables de Entorno para Railway

### Método 1: SendGrid API (Recomendado)
```bash
# En Railway Dashboard > Variables
SENDGRID_API_KEY=SG.tu_api_key_aqui
SENDGRID_FROM_EMAIL=noreply@tudominio.com
RECIPIENT_EMAIL=destinatario@gmail.com
```

### Método 2: Webhook Personalizado
```bash
EMAIL_WEBHOOK_URL=https://tu-webhook.com/send-email
SENDER_EMAIL=noreply@tudominio.com
RECIPIENT_EMAIL=destinatario@gmail.com
```

### Método 3: SMTP Tradicional (Respaldo)
```bash
SENDER_EMAIL=tu_email@gmail.com
SENDER_PASSWORD=tu_contraseña_de_aplicacion
RECIPIENT_EMAIL=destinatario@gmail.com
```

## 🚀 Configuración de SendGrid (Recomendado para Railway)

### 1. Crear Cuenta en SendGrid
- Ve a https://sendgrid.com/
- Crea una cuenta gratuita (100 emails/día gratis)
- Verifica tu email

### 2. Generar API Key
- Ve a Settings → API Keys
- Clic en "Create API Key"
- Nombre: "Railway FeedPro"
- Permisos: "Full Access" o "Mail Send"
- Copia la API Key generada

### 3. Configurar Dominio (Opcional pero Recomendado)
- Ve a Settings → Sender Authentication
- Configura "Single Sender Verification" con tu email
- O configura "Domain Authentication" si tienes dominio propio

### 4. Variables en Railway
```bash
# En Railway Dashboard > Variables
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SENDGRID_FROM_EMAIL=noreply@tudominio.com  # o tu email verificado
RECIPIENT_EMAIL=destinatario@gmail.com
```

## Configuración de Gmail para Railway (Método de Respaldo)

### 1. Habilitar 2FA en Gmail
- Ve a tu cuenta de Google
- Seguridad → Verificación en 2 pasos
- Activa la verificación en 2 pasos

### 2. Generar Contraseña de Aplicación
- Ve a Seguridad → Contraseñas de aplicaciones
- Selecciona "Correo" y "Otro (nombre personalizado)"
- Escribe "Railway FeedPro"
- Copia la contraseña de 16 caracteres generada
- Usa esta contraseña en SENDER_PASSWORD (sin espacios)

### 3. Configurar Variables en Railway
```bash
# En el dashboard de Railway, ve a Variables y agrega:
SENDER_EMAIL=tu_email@gmail.com
SENDER_PASSWORD=abcd efgh ijkl mnop  # (sin espacios reales)
RECIPIENT_EMAIL=destinatario@gmail.com
```

## Proveedores SMTP Soportados

El sistema ahora soporta múltiples proveedores automáticamente:

### Gmail
- Servidor: smtp.gmail.com
- Puerto: 587 (TLS) o 465 (SSL)
- Requiere contraseña de aplicación

### Outlook/Hotmail
- Servidor: smtp-mail.outlook.com
- Puerto: 587
- Usa la contraseña normal de la cuenta

### Yahoo
- Servidor: smtp.mail.yahoo.com
- Puerto: 587
- Requiere contraseña de aplicación

## Solución de Problemas en Railway

### Error: "SMTPConnectError"
- Railway puede bloquear conexiones SMTP salientes
- Verifica que Railway permita tráfico SMTP en el puerto 587/465
- Considera usar un servicio de email dedicado como SendGrid

### Error: "SMTPAuthenticationError"
- Verifica que uses contraseña de aplicación (no contraseña normal)
- Asegúrate que el email coincida con la cuenta de la contraseña

### Error: "Timeout"
- Railway puede tener timeouts de red más estrictos
- El sistema ahora usa timeouts de 30 segundos
- Prueba con diferentes puertos (587 vs 465)

## Alternativas para Railway

Si SMTP no funciona, considera estos servicios:

### SendGrid
```bash
# Variables para SendGrid
SENDGRID_API_KEY=tu_api_key
SENDGRID_FROM_EMAIL=noreply@tudominio.com
```

### Mailgun
```bash
# Variables para Mailgun
MAILGUN_API_KEY=tu_api_key
MAILGUN_DOMAIN=tu_dominio.mailgun.org
```

### Resend
```bash
# Variables para Resend
RESEND_API_KEY=tu_api_key
RESEND_FROM_EMAIL=noreply@tudominio.com
```

## Verificación de Funcionamiento

El sistema intentará automáticamente:
1. Gmail con TLS (puerto 587)
2. Gmail con SSL (puerto 465)
3. Outlook (si el email es de Outlook/Hotmail)
4. Yahoo (si el email es de Yahoo)

Los logs mostrarán qué proveedor funcionó o por qué fallaron todos.

## Logs de Depuración

Busca estos mensajes en los logs de Railway:
- `✅ Correo enviado exitosamente` - Funcionó correctamente
- `❌ Error de autenticación` - Problema con credenciales
- `❌ Error de conexión` - Railway bloquea SMTP
- `❌ Timeout` - Problema de red/firewall
