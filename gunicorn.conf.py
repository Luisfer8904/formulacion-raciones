"""
Configuración de Gunicorn optimizada para Railway
Soluciona problemas de timeout y mejora la estabilidad
"""
import os
import multiprocessing

# Configuración del servidor
bind = f"0.0.0.0:{os.environ.get('PORT', '8080')}"
workers = int(os.environ.get('WEB_CONCURRENCY', multiprocessing.cpu_count() * 2 + 1))

# Configuración de timeouts para Railway
timeout = 120  # 2 minutos (Railway tiene límites de tiempo)
keepalive = 5
worker_connections = 1000
max_requests = 1000  # Reiniciar workers después de 1000 requests
max_requests_jitter = 100  # Variación aleatoria para evitar reinicio simultáneo

# Configuración de workers
worker_class = "sync"  # Usar workers síncronos para mejor compatibilidad
worker_tmp_dir = "/dev/shm"  # Usar memoria compartida si está disponible

# Configuración de logging
loglevel = os.environ.get('LOG_LEVEL', 'info').lower()
accesslog = "-"  # Log a stdout
errorlog = "-"   # Log a stderr
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Configuración de proceso
preload_app = True  # Cargar aplicación antes de fork (mejor para Railway)
daemon = False
pidfile = None
tmp_upload_dir = None

# Configuración específica para Railway
def when_ready(server):
    """Callback cuando el servidor está listo"""
    print("🚀 Gunicorn iniciado correctamente en Railway")
    print(f"   Workers: {workers}")
    print(f"   Timeout: {timeout}s")
    print(f"   Puerto: {os.environ.get('PORT', '8080')}")

def worker_int(worker):
    """Callback cuando worker recibe SIGINT"""
    print(f"⚠️ Worker {worker.pid} interrumpido")

def on_exit(server):
    """Callback al salir"""
    print("👋 Gunicorn finalizando...")

def on_reload(server):
    """Callback al recargar"""
    print("🔄 Gunicorn recargando...")

# Configuración de memoria para Railway
def max_worker_memory():
    """Límite de memoria por worker (Railway tiene límites)"""
    return int(os.environ.get('MAX_WORKER_MEMORY', '512')) * 1024 * 1024  # 512MB por defecto

# Configuración de graceful shutdown
graceful_timeout = 30
