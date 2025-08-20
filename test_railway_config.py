#!/usr/bin/env python3
"""
Script de prueba para verificar la configuración de Railway
Ejecutar después del despliegue para validar que todo funcione
"""
import os
import requests
import json
from datetime import datetime

def test_health_endpoint(base_url):
    """Prueba el endpoint de health check"""
    print("🔍 Probando endpoint de health check...")
    
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check exitoso:")
            print(f"   Status: {data.get('status')}")
            print(f"   Database: {data.get('database')}")
            print(f"   Email configurado: {data.get('environment', {}).get('email_configured')}")
            print(f"   SendGrid configurado: {data.get('environment', {}).get('sendgrid_configured')}")
            return True
        else:
            print(f"❌ Health check falló: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error al probar health check: {e}")
        return False

def test_email_config():
    """Prueba la configuración de email localmente"""
    print("\n🔍 Verificando configuración de email...")
    
    # Variables críticas
    sendgrid_key = os.getenv('SENDGRID_API_KEY')
    sendgrid_email = os.getenv('SENDGRID_FROM_EMAIL')
    webhook_url = os.getenv('EMAIL_WEBHOOK_URL')
    sender_email = os.getenv('SENDER_EMAIL')
    
    print(f"   SENDGRID_API_KEY: {'✅ Configurado' if sendgrid_key else '❌ No configurado'}")
    print(f"   SENDGRID_FROM_EMAIL: {'✅ Configurado' if sendgrid_email else '❌ No configurado'}")
    print(f"   EMAIL_WEBHOOK_URL: {'✅ Configurado' if webhook_url else '⚠️ No configurado (opcional)'}")
    print(f"   SENDER_EMAIL (respaldo): {'✅ Configurado' if sender_email else '❌ No configurado'}")
    
    # Verificar que al menos un método esté configurado
    if sendgrid_key or webhook_url or sender_email:
        print("✅ Al menos un método de email está configurado")
        return True
    else:
        print("❌ Ningún método de email está configurado")
        return False

def test_sendgrid_api():
    """Prueba la API de SendGrid si está configurada"""
    print("\n🔍 Probando conexión con SendGrid...")
    
    api_key = os.getenv('SENDGRID_API_KEY')
    if not api_key:
        print("⚠️ SENDGRID_API_KEY no configurado, saltando prueba")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Probar endpoint de verificación de SendGrid
        response = requests.get(
            "https://api.sendgrid.com/v3/user/account",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Conexión con SendGrid exitosa")
            return True
        else:
            print(f"❌ Error en SendGrid: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error al probar SendGrid: {e}")
        return False

def generate_report():
    """Genera un reporte de la configuración"""
    print("\n📊 REPORTE DE CONFIGURACIÓN")
    print("=" * 50)
    
    # Información del entorno
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Puerto configurado: {os.getenv('PORT', 'No configurado')}")
    print(f"Nivel de log: {os.getenv('LOG_LEVEL', 'info')}")
    print(f"Workers: {os.getenv('WEB_CONCURRENCY', 'auto')}")
    
    # Variables de base de datos
    print(f"\nBase de datos:")
    print(f"   Host: {os.getenv('MYSQLHOST', 'No configurado')}")
    print(f"   Database: {os.getenv('MYSQLDATABASE', 'No configurado')}")
    print(f"   User: {os.getenv('MYSQLUSER', 'No configurado')}")
    
    # Configuración de email
    print(f"\nEmail:")
    print(f"   SendGrid API: {'✅' if os.getenv('SENDGRID_API_KEY') else '❌'}")
    print(f"   SendGrid From: {'✅' if os.getenv('SENDGRID_FROM_EMAIL') else '❌'}")
    print(f"   Webhook URL: {'✅' if os.getenv('EMAIL_WEBHOOK_URL') else '❌'}")
    print(f"   SMTP Email: {'✅' if os.getenv('SENDER_EMAIL') else '❌'}")
    print(f"   SMTP Password: {'✅' if os.getenv('SENDER_PASSWORD') else '❌'}")

def main():
    """Función principal de prueba"""
    print("🚀 PRUEBA DE CONFIGURACIÓN DE RAILWAY - FeedPro")
    print("=" * 60)
    
    # Obtener URL base
    base_url = input("Ingresa la URL de tu aplicación en Railway (ej: https://tu-app.railway.app): ").strip()
    if not base_url:
        print("❌ URL requerida para las pruebas")
        return
    
    # Remover trailing slash
    base_url = base_url.rstrip('/')
    
    # Ejecutar pruebas
    results = []
    
    print(f"\n🎯 Probando aplicación en: {base_url}")
    
    # Prueba 1: Health check
    results.append(("Health Check", test_health_endpoint(base_url)))
    
    # Prueba 2: Configuración de email
    results.append(("Email Config", test_email_config()))
    
    # Prueba 3: SendGrid API
    results.append(("SendGrid API", test_sendgrid_api()))
    
    # Generar reporte
    generate_report()
    
    # Resumen final
    print(f"\n🏁 RESUMEN DE PRUEBAS")
    print("=" * 30)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nResultado: {passed}/{len(results)} pruebas exitosas")
    
    if passed == len(results):
        print("🎉 ¡Todas las pruebas pasaron! La configuración está correcta.")
    else:
        print("⚠️ Algunas pruebas fallaron. Revisa la configuración en Railway.")
        print("\n💡 Pasos sugeridos:")
        print("1. Verifica las variables de entorno en Railway Dashboard")
        print("2. Configura SENDGRID_API_KEY si planeas usar SendGrid")
        print("3. Revisa los logs de Railway para más detalles")

if __name__ == "__main__":
    main()
