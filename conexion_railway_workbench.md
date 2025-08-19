# 🔗 Conectar MySQL Workbench a Railway

## Paso 1: Obtener credenciales de Railway

1. **Ve al panel de Railway** que tienes abierto
2. **Haz clic en el servicio MySQL** (mysql-production-15ea...)
3. **Ve a la pestaña "Variables"** o "Connect"
4. **Busca estas variables:**
   - `MYSQLHOST` (Host/Servidor)
   - `MYSQLPORT` (Puerto, usualmente 3306)
   - `MYSQLDATABASE` (Nombre de la base de datos)
   - `MYSQLUSER` (Usuario)
   - `MYSQLPASSWORD` (Contraseña)

## Paso 2: Configurar MySQL Workbench

1. **Abre MySQL Workbench**
2. **Haz clic en el "+" junto a "MySQL Connections"**
3. **Configura la conexión:**

### Configuración de la conexión:
```
Connection Name: Railway - FeedPro
Connection Method: Standard (TCP/IP)
Hostname: [MYSQLHOST de Railway]
Port: [MYSQLPORT de Railway] (usualmente 3306)
Username: [MYSQLUSER de Railway]
Password: [MYSQLPASSWORD de Railway]
Default Schema: [MYSQLDATABASE de Railway]
```

## Paso 3: Probar la conexión

1. **Haz clic en "Test Connection"**
2. **Si es exitosa, haz clic en "OK"**
3. **Haz doble clic en la nueva conexión para conectarte**

## Paso 4: Ejecutar el SQL

Una vez conectado:
1. **Abre una nueva pestaña de Query**
2. **Copia y pega el contenido del archivo `railway_actividades.sql`**
3. **Ejecuta el SQL** (Ctrl+Shift+Enter o botón ⚡)

## Notas importantes:
- Railway usa SSL por defecto, si hay problemas de conexión, ve a "Advanced" y configura SSL
- El host de Railway suele ser algo como: `containers-us-west-xxx.railway.app`
- El puerto puede ser diferente a 3306 en Railway
