from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.db import get_db_connection
from typing import Any
import numpy as np
from scipy.optimize import minimize

optimizacion_bp = Blueprint('optimizacion_bp', __name__)

def formatear_inclusion(valor):
    """Formatear inclusiones con decimales inteligentes"""
    num = float(valor)
    
    # Si el valor es menor a 0.01, usar 4 decimales
    if num < 0.01 and num > 0:
        return round(num, 4)
    # Si el valor es menor a 0.1, usar 3 decimales
    elif num < 0.1:
        return round(num, 3)
    # Para valores mayores, usar 2 decimales
    else:
        return round(num, 2)

@optimizacion_bp.route('/formulacion_minerales')
def formulacion_minerales():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para acceder.', 'error')
        return redirect(url_for('auth_bp.login'))

    # Obtener mezcla_id si viene como parámetro de consulta (query string)
    mezcla_id = request.args.get('mezcla_id', default=None, type=int)

    conn = get_db_connection()
    
    cursor = conn.cursor(dictionary=True)
    
    # Configuraciones del usuario - por ahora usar valores por defecto
    # TODO: Implementar consulta a base de datos cuando se resuelvan los tipos
    moneda = 'HNL'
    unidad_medida = 'kg'
    tipo_moneda = 'Nacional'

    # Obtener todos los ingredientes
    cursor.execute("SELECT id, nombre, comentario, ms, precio FROM ingredientes WHERE usuario_id = %s", (session['user_id'],))
    ingredientes_raw = cursor.fetchall()

    # Obtener todos los nutrientes disponibles filtrados por usuario (incluyendo id y unidad)
    cursor.execute("SELECT id, nombre, unidad FROM nutrientes WHERE usuario_id = %s", (session['user_id'],))
    nutrientes_info = cursor.fetchall()

    ingredientes = []
    for ing in ingredientes_raw:
        ing_typed: Any = ing
        ingrediente = {
            'id': ing_typed['id'],
            'nombre': ing_typed['nombre'],
            'precio': ing_typed.get('precio', 0.0) if hasattr(ing_typed, 'get') else 0.0,
            'comentario': ing_typed.get('comentario', '') if hasattr(ing_typed, 'get') else '',
            'ms': ing_typed.get('ms', 100) if hasattr(ing_typed, 'get') else 100,
            'nutrientes': []
        }
        for nutriente in nutrientes_info:
            nutriente_typed: Any = nutriente
            cursor.execute("""
                SELECT inut.valor 
                FROM ingredientes_nutrientes AS inut
                WHERE inut.ingrediente_id = %s AND inut.nutriente_id = %s
            """, (ing_typed['id'], nutriente_typed['id']))
            result: Any = cursor.fetchone()
            valor = result['valor'] if result else 0.0
            ingrediente['nutrientes'].append({
                'id': nutriente_typed['id'],
                'nombre': nutriente_typed['nombre'],
                'valor': valor
            })
            ingrediente[str(nutriente_typed['nombre'])] = valor
        ingredientes.append(ingrediente)

    # Obtener mezclas disponibles para el usuario (para mostrar en el formulario)
    cursor.execute("SELECT id, nombre FROM mezclas WHERE usuario_id = %s ORDER BY nombre ASC", (session['user_id'],))
    mezclas_disponibles = cursor.fetchall()

    # === BLOQUE NUEVO: obtener mezcla seleccionada y sus ingredientes si mezcla_id existe ===
    mezcla = None
    ingredientes_mezcla = []
    if mezcla_id:
        cursor.execute("SELECT * FROM mezclas WHERE id = %s AND usuario_id = %s", (mezcla_id, session['user_id']))
        mezcla_result: Any = cursor.fetchone()
        mezcla = mezcla_result

        if mezcla:
            cursor.execute("""
                SELECT mi.*, i.nombre AS nombre_ingrediente, i.precio, i.ms
                FROM mezcla_ingredientes mi
                JOIN ingredientes i ON mi.ingrediente_id = i.id
                WHERE mi.mezcla_id = %s
            """, (mezcla_id,))
            ingredientes_mezcla = cursor.fetchall()

    cursor.close()
    conn.close()

    # Pasar mezcla_id a la plantilla si es necesario para uso futuro
    return render_template('operaciones/formulacion_minerales.html',
                           minerales=ingredientes,
                           nutrientes=nutrientes_info,
                           mezclas_disponibles=mezclas_disponibles,
                           mezcla=mezcla,
                           ingredientes_mezcla=ingredientes_mezcla,
                           config_usuario={
                               'moneda': moneda,
                               'unidad_medida': unidad_medida,
                               'tipo_moneda': tipo_moneda
                           })

@optimizacion_bp.route('/api/requerimientos_usuario', methods=['GET'])
def obtener_requerimientos_usuario():
    """Obtener todos los requerimientos del usuario actual"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, nombre, tipo_especie, comentario
            FROM requerimientos
            WHERE usuario_id = %s
            ORDER BY nombre ASC
        """, (session['user_id'],))
        
        requerimientos = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Retornar directamente la lista de requerimientos (sin wrapper)
        return jsonify(requerimientos)
        
    except Exception as e:
        print("❌ Error al obtener requerimientos:", e)
        return jsonify({'error': 'Error al cargar requerimientos'}), 500

@optimizacion_bp.route('/api/requerimiento/<int:requerimiento_id>/nutrientes', methods=['GET'])
def obtener_nutrientes_requerimiento(requerimiento_id):
    """Obtener nutrientes asociados a un requerimiento específico"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que el requerimiento pertenece al usuario
        cursor.execute("""
            SELECT id FROM requerimientos 
            WHERE id = %s AND usuario_id = %s
        """, (requerimiento_id, session['user_id']))
        
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'error': 'Requerimiento no encontrado'}), 404
        
        # Obtener nutrientes del requerimiento con sus valores sugeridos
        cursor.execute("""
            SELECT n.id as nutriente_id, n.nombre, n.unidad, n.tipo, 
                   cr.valor_sugerido
            FROM nutrientes n
            INNER JOIN conjuntos_requerimientos cr ON n.id = cr.nutriente_id
            WHERE cr.requerimiento_id = %s AND n.usuario_id = %s
            ORDER BY n.nombre ASC
        """, (requerimiento_id, session['user_id']))
        
        nutrientes = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Retornar directamente la lista de nutrientes (sin wrapper)
        return jsonify(nutrientes)
        
    except Exception as e:
        print("❌ Error al obtener nutrientes del requerimiento:", e)
        return jsonify({'error': 'Error al cargar nutrientes'}), 500

@optimizacion_bp.route('/optimizar_formulacion', methods=['POST'])
def optimizar_formulacion():
    print("🚀 INICIANDO OPTIMIZACIÓN PASO A PASO")
    
    data = request.get_json()
    print("🛠️ Datos recibidos del frontend:", data)

    ingredientes = data.get('ingredientes', [])
    requerimientos = data.get('requerimientos', [])

    if not ingredientes or not requerimientos:
        print("❌ Error: Ingredientes o requerimientos vacíos")
        return jsonify({'error': 'Datos incompletos'}), 400

    # Validar que los ingredientes tengan estructura de nutrientes (pero pueden tener valores 0)
    for ing in ingredientes:
        nutrientes = ing.get('aporte')
        if not nutrientes or not isinstance(nutrientes, dict):
            print(f"⚠️ Advertencia: El ingrediente {ing['nombre']} no tiene estructura de nutrientes válida. Se asignará estructura vacía.")
            # En lugar de fallar, asignar una estructura vacía de nutrientes
            ing['aporte'] = {}
            # Agregar nutrientes con valor 0 para todos los requerimientos
            for req in requerimientos:
                ing['aporte'][req['nombre']] = 0.0

    print("\n" + "="*60)
    print("PASO 1: AJUSTAR LA SUMA A 100%")
    print("="*60)
    
    # Preparar datos básicos
    costos = []
    bounds_ingredientes = []
    matriz_nutrientes = []
    
    for ing in ingredientes:
        costos.append(float(ing.get('costo', 0)))
        limite_min = float(ing.get('limite_min', 0))
        limite_max = float(ing.get('limite_max', 100))
        
        # Debug: mostrar datos recibidos
        print(f"🔍 Datos ingrediente {ing['nombre']}:")
        print(f"   - limite_min: {limite_min}")
        print(f"   - limite_max: {limite_max}")
        print(f"   - costo: {costos[-1]}")
        
        # Si los límites son 0, omitir la regla (usar valores por defecto)
        if limite_min == 0 and limite_max == 0:
            print(f"⚠️ Omitiendo límites para {ing['nombre']} (min=0, max=0)")
            bounds_ingredientes.append((0, 100))  # Valores por defecto
        else:
            bounds_ingredientes.append((limite_min, limite_max))
        
        print(f"📊 {ing['nombre']}: bounds=({bounds_ingredientes[-1][0]}, {bounds_ingredientes[-1][1]}), costo={costos[-1]}")

    # Verificar que la suma de límites máximos permita llegar a 100%
    suma_maximos = sum(bound[1] for bound in bounds_ingredientes)
    if suma_maximos < 100:
        print(f"❌ Error: La suma de límites máximos ({suma_maximos}%) no llega al 100%")
        return jsonify({'error': 'Los límites máximos de ingredientes no permiten una mezcla que sume 100%'}), 400

    print(f"✅ Suma de límites máximos: {suma_maximos}% (≥100%)")

    print("\n" + "="*60)
    print("PASO 2: VALIDAR LÍMITES MÍNIMOS Y MÁXIMOS DE INGREDIENTES")
    print("="*60)
    
    # Verificar que los límites mínimos no excedan 100%
    suma_minimos = sum(bound[0] for bound in bounds_ingredientes)
    if suma_minimos > 100:
        print(f"❌ Error: La suma de límites mínimos ({suma_minimos}%) excede el 100%")
        return jsonify({'error': 'Los límites mínimos de ingredientes exceden el 100%'}), 400
    
    print(f"✅ Suma de límites mínimos: {suma_minimos}% (≤100%)")
    
    # Validar que cada límite mínimo sea menor o igual al máximo
    for i, (ing, bound) in enumerate(zip(ingredientes, bounds_ingredientes)):
        if bound[0] > bound[1]:
            print(f"❌ Error: {ing['nombre']} tiene límite mínimo ({bound[0]}%) mayor al máximo ({bound[1]}%)")
            return jsonify({'error': f"Límite mínimo de {ing['nombre']} es mayor al máximo"}), 400
        print(f"✅ {ing['nombre']}: {bound[0]}% ≤ {bound[1]}%")

    print("\n" + "="*60)
    print("PASO 3: AJUSTAR LÍMITES MÍNIMOS Y MÁXIMOS DE NUTRIENTES")
    print("="*60)
    
    # Construir matriz de nutrientes (USANDO VALORES EN BASE SECA: valor_bs)
    for req in requerimientos:
        fila = []
        for ing in ingredientes:
            nutrientes = ing.get('aporte', {})
            valor_nutriente = 0
            if req['nombre'].lower() == 'fósforo' or req['nombre'].lower() == 'fosforo':
                # Calcular fósforo en base seca: inclusion * fosforo * (ms / 100)
                # fosforo = valor del nutriente, ms = materia seca del ingrediente
                fosforo = 0.0
                ms = float(ing.get('ms', 100))
                inclusion = 1.0  # Inclusion será multiplicada en la optimización, por ahora 1
                if isinstance(nutrientes.get(req['nombre']), dict):
                    fosforo = float(nutrientes.get(req['nombre'], {}).get('valor', 0))
                else:
                    fosforo = float(nutrientes.get(req['nombre'], 0))
                # El valor base seca por unidad de inclusión:
                valor_nutriente = fosforo * (ms / 100)
            else:
                if isinstance(nutrientes.get(req['nombre']), dict):
                    valor_nutriente = float(nutrientes.get(req['nombre'], {}).get('valor_bs', 0))
                else:
                    valor_nutriente = float(nutrientes.get(req['nombre'] + '_bs', nutrientes.get(req['nombre'], 0)))
            fila.append(valor_nutriente)
        matriz_nutrientes.append(fila)
        print(f"🧪 {req['nombre']} (base seca): aportes por ingrediente = {fila}")

    # Procesar requerimientos de nutrientes
    restricciones_nutrientes = []
    
    for i, req in enumerate(requerimientos):
        req_min = req.get('min')
        req_max = req.get('max')
        nombre_nutriente = req['nombre']

        # Convertir valores vacíos o None a números
        if req_min in [None, '', 0]:
            req_min = 0
            print(f"⚠️ Omitiendo límite mínimo para {nombre_nutriente} (valor = 0)")
        else:
            req_min = float(req_min)

        if req_max in [None, '', 0]:
            req_max = None  # No aplicar límite máximo
            print(f"⚠️ Omitiendo límite máximo para {nombre_nutriente} (valor = 0)")
        else:
            req_max = float(req_max)

        # Crear funciones de restricción con closure correcto (USANDO BASE SECA)
        if req_min > 0:
            def crear_restriccion_min(indice, valor_min):
                return lambda x: np.dot(matriz_nutrientes[indice], x) / 100 - valor_min

            restricciones_nutrientes.append({
                'type': 'ineq',
                'fun': crear_restriccion_min(i, req_min)
            })
            print(f"✅ Restricción mínima para {nombre_nutriente} (base seca): ≥ {req_min}")

        if req_max is not None:
            def crear_restriccion_max(indice, valor_max):
                return lambda x: valor_max - np.dot(matriz_nutrientes[indice], x) / 100

            restricciones_nutrientes.append({
                'type': 'ineq',
                'fun': crear_restriccion_max(i, req_max)
            })
            print(f"✅ Restricción máxima para {nombre_nutriente} (base seca): ≤ {req_max}")

    print("\n" + "="*60)
    print("PASO 4: OPTIMIZACIÓN DE COSTO MÍNIMO")
    print("="*60)
    
    # Función objetivo: minimizar costo
    def objetivo(x):
        costo_total = np.dot(costos, x)
        return costo_total

    # Restricción principal: suma debe ser 100%
    restriccion_suma = {'type': 'eq', 'fun': lambda x: np.sum(x) - 100}
    
    # Combinar todas las restricciones
    todas_restricciones = [restriccion_suma] + restricciones_nutrientes
    
    print(f"🔧 Total de restricciones: {len(todas_restricciones)}")
    print(f"🎯 Función objetivo: minimizar costo total")
    
    # Intentar múltiples puntos iniciales para encontrar mejor solución
    mejores_resultados = []
    
    # Punto inicial 1: distribución uniforme
    x0_1 = np.array([100.0 / len(ingredientes)] * len(ingredientes))
    
    # Punto inicial 2: priorizar ingredientes de menor costo
    costos_ordenados = sorted(enumerate(costos), key=lambda x: x[1])
    x0_2 = np.zeros(len(ingredientes))
    for i, (idx, _) in enumerate(costos_ordenados):
        if i == 0:  # Ingrediente más barato
            x0_2[idx] = min(80, bounds_ingredientes[idx][1])
        else:
            x0_2[idx] = max(bounds_ingredientes[idx][0], 20.0 / (len(ingredientes) - 1))
    
    # Punto inicial 3: usar límites mínimos como base
    x0_3 = np.array([bound[0] for bound in bounds_ingredientes])
    suma_minimos = np.sum(x0_3)
    if suma_minimos < 100:
        # Distribuir el resto proporcionalmente
        resto = 100 - suma_minimos
        for i in range(len(x0_3)):
            disponible = bounds_ingredientes[i][1] - x0_3[i]
            if disponible > 0:
                x0_3[i] += resto * (disponible / sum(max(0, bounds_ingredientes[j][1] - x0_3[j]) for j in range(len(x0_3))))
    
    puntos_iniciales = [x0_1, x0_2, x0_3]
    nombres_puntos = ["Uniforme", "Menor costo", "Límites mínimos"]
    
    for idx, (x0, nombre) in enumerate(zip(puntos_iniciales, nombres_puntos)):
        # Ajustar punto inicial para respetar bounds
        for i, bound in enumerate(bounds_ingredientes):
            if x0[i] < bound[0]:
                x0[i] = bound[0]
            elif x0[i] > bound[1]:
                x0[i] = bound[1]
        
        # Normalizar para que sume 100
        suma_actual = np.sum(x0)
        if suma_actual > 0:
            x0 = x0 * (100.0 / suma_actual)
            # Verificar bounds después de normalizar
            for i, bound in enumerate(bounds_ingredientes):
                if x0[i] < bound[0]:
                    x0[i] = bound[0]
                elif x0[i] > bound[1]:
                    x0[i] = bound[1]
        
        print(f"🚀 Punto inicial {idx+1} ({nombre}): {x0}")
        
        # Ejecutar optimización
        print(f"⚙️ Ejecutando optimización {idx+1}...")
        resultado = minimize(
            objetivo, 
            x0, 
            method='SLSQP', 
            bounds=bounds_ingredientes, 
            constraints=todas_restricciones,
            options={'disp': False, 'maxiter': 2000, 'ftol': 1e-9}
        )
        
        if resultado.success:
            costo_resultado = resultado.fun
            print(f"✅ Optimización {idx+1} exitosa - Costo: ${costo_resultado:.4f}")
            mejores_resultados.append((resultado, costo_resultado, nombre))
        else:
            print(f"❌ Optimización {idx+1} falló: {resultado.message}")
    
    # Seleccionar el mejor resultado
    if not mejores_resultados:
        print("❌ Ninguna optimización fue exitosa")
        return jsonify({
            'error': 'No se pudo encontrar una solución factible. Revisa que los límites sean compatibles.'
        }), 400
    
    # Ordenar por costo (menor es mejor)
    mejores_resultados.sort(key=lambda x: x[1])
    resultado, mejor_costo, mejor_metodo = mejores_resultados[0]
    
    print(f"🏆 Mejor resultado obtenido con método: {mejor_metodo}")
    
    print(f"📊 Resultado de optimización: {resultado.success}")
    print(f"📊 Mensaje: {resultado.message}")
    
    # === BLOQUE DE VALIDACIÓN DE NUTRIENTES (USANDO BASE SECA) ===
    # Generar los resultados de nutrientes de la mezcla optimizada en base seca
    resultados_nutrientes = {}
    for idx_req, req in enumerate(requerimientos):
        nombre_nutriente = req['nombre']
        valor = 0.0
        # DEBUG: imprimir aportes por ingrediente para fósforo
        if nombre_nutriente.lower() == 'fósforo' or nombre_nutriente.lower() == 'fosforo':
            print("🧮 Aportes de fósforo por ingrediente (antes de restricción mínima):")
            for idx_ing, ing in enumerate(ingredientes):
                ms = float(ing.get('ms', 100))
                inclusion = resultado.x[idx_ing]
                nutrientes = ing.get('aporte', {})
                if isinstance(nutrientes.get(nombre_nutriente), dict):
                    fosforo = float(nutrientes.get(nombre_nutriente, {}).get('valor', 0))
                else:
                    fosforo = float(nutrientes.get(nombre_nutriente, 0))
                print(f"Ingrediente: {ing['nombre']}, MS: {ms}, Fósforo: {fosforo}, Inclusión: {inclusion}")
        for idx_ing, ing in enumerate(ingredientes):
            nutrientes = ing.get('aporte', {})
            inclusion = resultado.x[idx_ing]
            if nombre_nutriente.lower() == 'fósforo' or nombre_nutriente.lower() == 'fosforo':
                # Calcular fósforo en base seca: inclusion * fosforo * (ms / 100)
                ms = float(ing.get('ms', 100))
                if isinstance(nutrientes.get(nombre_nutriente), dict):
                    fosforo = float(nutrientes.get(nombre_nutriente, {}).get('valor', 0))
                else:
                    fosforo = float(nutrientes.get(nombre_nutriente, 0))
                aporte_base_seca = inclusion * fosforo * (ms / 100)
                valor += aporte_base_seca  # Sin división adicional por 100
            else:
                if isinstance(nutrientes.get(nombre_nutriente), dict):
                    aporte_nutriente = float(nutrientes.get(nombre_nutriente, {}).get('valor_bs', 0))
                else:
                    aporte_nutriente = float(nutrientes.get(nombre_nutriente + '_bs', nutrientes.get(nombre_nutriente, 0)))
                valor += aporte_nutriente * inclusion  # Sin división adicional por 100
        resultados_nutrientes[nombre_nutriente] = valor

    # Validar si se cumplen los mínimos y máximos de nutrientes antes de evaluar el éxito de la optimización
    for nutriente in resultados_nutrientes:
        resultado_valor = resultados_nutrientes[nutriente]
        minimo_requerido = None
        maximo_requerido = None
        for req in requerimientos:
            if req['nombre'] == nutriente:
                minimo_requerido = req.get('min', None)
                maximo_requerido = req.get('max', None)
                break
        # Validación de mínimo
        if minimo_requerido is not None and minimo_requerido != '' and float(minimo_requerido) > 0:
            if resultado_valor < float(minimo_requerido):
                print(f"⚠️ Nutriente {nutriente} por debajo del mínimo. Obtenido: {resultado_valor:.4f} vs requerido: {minimo_requerido}")
        # Validación de máximo
        if maximo_requerido is not None and maximo_requerido != '' and float(maximo_requerido) > 0:
            if resultado_valor > float(maximo_requerido):
                print(f"⚠️ Nutriente {nutriente} por encima del máximo. Obtenido: {resultado_valor:.4f} vs máximo permitido: {maximo_requerido}")

    # Ahora, validar si la optimización fue exitosa (minimización del costo)
    if not resultado.success:
        print("❌ Error: Optimización no exitosa")
        return jsonify({'error': 'No se pudo optimizar la mezcla'}), 400

    print("\n" + "="*60)
    print("✅ OPTIMIZACIÓN EXITOSA")
    print("="*60)
    
    resultado_lista = []
    costo_total = 0
    
    for i, inclusion in enumerate(resultado.x):
        costo_ingrediente = inclusion * costos[i] / 100
        costo_total += costo_ingrediente
        
        resultado_lista.append({
            'ingrediente': ingredientes[i]['nombre'],
            'inclusion': formatear_inclusion(inclusion),
            'peso': formatear_inclusion(inclusion),  # Para mezcla de 100 kg
            'valor': round(costo_ingrediente, 2)
        })
        
        print(f"📋 {ingredientes[i]['nombre']}: {inclusion:.2f}% (${costo_ingrediente:.2f})")
    
    print(f"💰 Costo total optimizado: ${costo_total:.2f}")
    
    # Verificar que la suma sea 100%
    suma_final = sum(r['inclusion'] for r in resultado_lista)
    print(f"✅ Suma final: {suma_final:.2f}%")

    return jsonify({
        'resultado': resultado_lista, 
        'costo_total': round(costo_total, 2),
        'mensaje': 'Optimización completada exitosamente'
    })
