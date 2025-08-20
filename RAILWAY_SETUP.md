# 🚀 Configuración de Variables de Entorno para Railway

## Variables Requeridas para Corregir los Errores

### 1. Variables de Email (CRÍTICAS - Faltan en Railway)

```bash
# Método 1: SendGrid API (RECOMENDADO para Railway)
SENDGRID_API_KEY=SG.tu_api_key_de_sendgrid_aqui
SENDGRID_FROM_EMAIL=noreply@tudominio.com

# Método 2: Webhook personalizado (ALTERNATIVO)
EMAIL_WEBHOOK_URL=https://tu-webhook-service.com/send-email

# Variables ya configuradas (SMTP Gmail - Respaldo)
SENDER_EMAIL=feedpro07@gmail.com
SENDER_PASSWORD=hfawobjfxrtkaapi
RECIPIENT_EMAIL=lfrivera8904@gmail.com
```

### 2. Variables de Configuración de Gunicorn

```bash
# Configuración de workers (opcional - usa valores por defecto si no se define)
WEB_CONCURRENCY=2
LOG_LEVEL=info
MAX_WORKER_MEMORY=512

# Puerto (Railway lo configura automáticamente)
PORT=8080
```

### 3. Variables de Base de Datos (Ya configuradas por Railway)

```bash
# Estas son configuradas automáticamente por Railway
MYSQLHOST=containers-us-west-xxx.railway.app
MYSQLPORT=3306
MYSQLDATABASE=railway
MYSQLUSER=root
MYSQLPASSWORD=tu_password_de_railway
```

## 🔧 Pasos para Configurar en Railway

### Paso 1: Configurar SendGrid (SOLUCIÓN RECOMENDADA)

1. **Crear cuenta en SendGrid:**
   - Ve a https://sendgrid.com/
   - Regístrate (plan gratuito: 100 emails/día)
   - Verifica tu email

2. **Generar API Key:**
   - Settings → API Keys → Create API Key
   - Nombre: "Railway FeedPro"
   - Permisos: "Full Access"
   - Copia la API Key generada

3. **Configurar en Railway:**
   ```bash
   # En Railway Dashboard → tu-proyecto → Variables
   SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   SENDGRID_FROM_EMAIL=noreply@tudominio.com  # o tu email verificado
   ```

### Paso 2: Configurar Webhook (ALTERNATIVO)

Si prefieres usar un webhook personalizado:

```bash
# En Railway Dashboard → Variables
EMAIL_WEBHOOK_URL=https://tu-servicio-webhook.com/send-email
```

### Paso 3: Variables de Rendimiento (OPCIONAL)

Para optimizar el rendimiento en Railway:

```bash
# En Railway Dashboard → Variables
WEB_CONCURRENCY=2          # Número de workers
LOG_LEVEL=info            # Nivel de logging
MAX_WORKER_MEMORY=512     # Memoria máxima por worker (MB)
```

## 🚨 Problemas Identificados y Soluciones

### Problema 1: Worker Timeout
**Error:** `WORKER TIMEOUT (pid:2)`
**Solución:** ✅ Configuración de Gunicorn optimizada (gunicorn.conf.py)

### Problema 2: Email no se envía
**Error:** `❌ SENDGRID_API_KEY no configurado`
**Solución:** ⚠️ Configurar SENDGRID_API_KEY en Railway

### Problema 3: Webhook no configurado
**Error:** `❌ EMAIL_WEBHOOK_URL no configurado`
**Solución:** ⚠️ Configurar EMAIL_WEBHOOK_URL o usar SendGrid

## 🔍 Verificación de Configuración

### Health Check Endpoint
Después del despliegue, verifica que todo funcione:

```bash
curl https://tu-app.railway.app/health
```

Respuesta esperada:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-20T12:00:00",
  "database": "ok",
  "environment": {
    "port": "8080",
    "email_configured": true,
    "sendgrid_configured": true
  },
  "version": "1.0.0"
}
```

### Logs de Railway
Busca estos mensajes en los logs:

```bash
# Éxito
✅ Gunicorn iniciado correctamente en Railway
✅ Correo enviado exitosamente via SendGrid

# Errores a corregir
❌ SENDGRID_API_KEY no configurado
❌ EMAIL_WEBHOOK_URL no configurado
```

## 📋 Checklist de Configuración

- [ ] **SENDGRID_API_KEY** configurado en Railway
- [ ] **SENDGRID_FROM_EMAIL** configurado en Railway
- [ ] Verificar que SendGrid esté funcionando
- [ ] Probar endpoint `/health` después del despliegue
- [ ] Monitorear logs para confirmar que no hay más timeouts
- [ ] Probar envío de emails desde la aplicación

## 🆘 Soporte

Si necesitas ayuda:
1. Verifica los logs de Railway
2. Prueba el endpoint `/health`
3. Revisa que todas las variables estén configuradas
4. Contacta soporte si persisten los problemas

---

**Nota:** Las variables SENDER_EMAIL, SENDER_PASSWORD y RECIPIENT_EMAIL ya están configuradas como respaldo SMTP, pero SendGrid es más confiable en Railway.
