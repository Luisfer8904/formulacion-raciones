import requests
import json

# Datos de prueba para el optimizador
test_data = {
    "ingredientes": [
        {
            "nombre": "Maíz",
            "limite_min": 0,
            "limite_max": 70,
            "costo": 0.50,
            "aporte": {
                "Proteína": 8.5,
                "Energía": 3200
            }
        },
        {
            "nombre": "Soya",
            "limite_min": 0,
            "limite_max": 40,
            "costo": 1.20,
            "aporte": {
                "Proteína": 44.0,
                "Energía": 2800
            }
        },
        {
            "nombre": "Availa",
            "limite_min": 0,
            "limite_max": 10,
            "costo": 5.00,
            "aporte": {
                "Proteína": 0,
                "Energía": 0
            }
        }
    ],
    "requerimientos": [
        {
            "nombre": "Proteína",
            "min": 16,
            "max": 20,
            "unidad": "%"
        },
        {
            "nombre": "Energía",
            "min": 2900,
            "max": 3100,
            "unidad": "kcal/kg"
        }
    ]
}

# Enviar solicitud al optimizador
url = "http://localhost:5001/optimizar_formulacion"
headers = {'Content-Type': 'application/json'}

print("🧪 Enviando datos de prueba al optimizador...")
print("📊 Datos enviados:")
print(json.dumps(test_data, indent=2, ensure_ascii=False))

try:
    response = requests.post(url, json=test_data, headers=headers)
    
    print(f"\n📡 Código de respuesta: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Optimización exitosa!")
        print("📋 Resultado:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("❌ Error en optimización:")
        print(response.text)
        
except Exception as e:
    print(f"❌ Error de conexión: {e}")
