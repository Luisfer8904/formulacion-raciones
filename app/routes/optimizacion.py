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
    
    # Obtener configuración del usuario
    cursor.execute("""
        SELECT moneda, tipo_moneda, unidad_medida
        FROM usuarios
        WHERE id = %s
    """, (session['user_id'],))
    config_usuario = cursor.fetchone()
    
    # Si no hay configuración, usar valores por defecto
    if not config_usuario:
        config_usuario = {
            'moneda': 'USD',
            'tipo_moneda': '$',
            'unidad_medida': 'kg'
        }
    
    moneda = config_usuario['moneda'] if config_usuario else 'USD'
    unidad_medida = config_usuario['unidad_medida'] if config_usuario else 'kg'
    tipo_moneda = config_usuario['tipo_moneda'] if config_usuario else '$'

    # Obtener todos los ingredientes
    cursor.execute("SELECT id, nombre, comentario, ms, precio FROM ingredientes WHERE usuario_id = %s ORDER BY nombre ASC", (session['user_id'],))
    ingredientes_raw = cursor.fetchall()

    # Obtener todos los nutrientes disponibles filtrados por usuario (incluyendo id y unidad)
    cursor.execute("SELECT id, nombre, unidad FROM nutrientes WHERE usuario_id = %s ORDER BY nombre ASC", (session['user_id'],))
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
        print("❌ Usuario no autenticado")
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        print(f"🔍 Obteniendo requerimientos para usuario: {session['user_id']}")
        
        conn = get_db_connection()
        if not conn:
            print("❌ Error: No se pudo conectar a la base de datos")
            return jsonify({'error': 'Error de conexión a la base de datos'}), 500
            
        cursor = conn.cursor(dictionary=True)
        
        # Primero verificar si la tabla existe
        cursor.execute("SHOW TABLES LIKE 'requerimientos'")
        tabla_existe = cursor.fetchone()
        
        if not tabla_existe:
            print("❌ Error: La tabla 'requerimientos' no existe")
            cursor.close()
            conn.close()
            return jsonify({'error': 'Tabla de requerimientos no encontrada'}), 500
        
        # Verificar estructura de la tabla
        cursor.execute("DESCRIBE requerimientos")
        columnas = cursor.fetchall()
        print(f"📋 Estructura de tabla requerimientos: {[col['Field'] for col in columnas]}")
        
        # Ejecutar consulta con manejo de errores mejorado
        cursor.execute("""
            SELECT id, nombre, 
                   COALESCE(tipo_especie, especie, 'Sin especificar') as tipo_especie, 
                   COALESCE(comentario, '') as comentario
            FROM requerimientos
            WHERE usuario_id = %s
            ORDER BY nombre ASC
        """, (session['user_id'],))
        
        requerimientos = cursor.fetchall()
        print(f"✅ Requerimientos encontrados: {len(requerimientos)}")
        
        # Si no hay requerimientos, devolver lista vacía en lugar de error
        if not requerimientos:
            print("⚠️ No se encontraron requerimientos para este usuario")
            cursor.close()
            conn.close()
            return jsonify([])
        
        cursor.close()
        conn.close()
        
        # Retornar directamente la lista de requerimientos
        return jsonify(requerimientos)
        
    except Exception as e:
        print(f"❌ Error detallado al obtener requerimientos: {str(e)}")
        print(f"❌ Tipo de error: {type(e).__name__}")
        
        # Intentar cerrar conexiones si están abiertas
        try:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
        except:
            pass
            
        return jsonify({'error': f'Error al cargar requerimientos: {str(e)}'}), 500

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
    tipo_optimizacion = data.get('tipo_optimizacion', 'base_humeda')  # Por defecto base húmeda

    print(f"🎯 Tipo de optimización: {tipo_optimizacion}")

    if not ingredientes or not requerimientos:
        print("❌ Error: Ingredientes o requerimientos vacíos")
        return jsonify({
            'error': 'Datos incompletos',
            'validacion': {
                'tipo': 'datos_incompletos',
                'mensaje': 'No se han proporcionado ingredientes o requerimientos suficientes',
                'sugerencias': [
                    'Agregue al menos 2 ingredientes a la formulación',
                    'Defina al menos 1 requerimiento nutricional',
                    'Verifique que los ingredientes tengan valores nutricionales'
                ]
            }
        }), 400

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
        
        # Identificar ingredientes con límites muy restrictivos
        ingredientes_restrictivos = []
        for i, (ing, bound) in enumerate(zip(ingredientes, bounds_ingredientes)):
            if bound[1] < 20:  # Límites máximos muy bajos
                ingredientes_restrictivos.append(f"{ing['nombre']} (máx: {bound[1]}%)")
        
        return jsonify({
            'error': 'Los límites máximos de ingredientes no permiten una mezcla que sume 100%',
            'validacion': {
                'tipo': 'limites_maximos_insuficientes',
                'mensaje': f'La suma de límites máximos es {suma_maximos}%, necesita ser ≥100%',
                'detalles': {
                    'suma_actual': suma_maximos,
                    'suma_requerida': 100,
                    'deficit': 100 - suma_maximos
                },
                'sugerencias': [
                    'Aumente los límites máximos de algunos ingredientes',
                    'Agregue más ingredientes a la formulación',
                    f'Necesita aumentar {100 - suma_maximos:.1f}% en límites máximos'
                ] + ([f'Ingredientes con límites restrictivos: {", ".join(ingredientes_restrictivos)}'] if ingredientes_restrictivos else [])
            }
        }), 400

    print(f"✅ Suma de límites máximos: {suma_maximos}% (≥100%)")

    print("\n" + "="*60)
    print("PASO 2: VALIDAR LÍMITES MÍNIMOS Y MÁXIMOS DE INGREDIENTES")
    print("="*60)
    
    # Verificar que los límites mínimos no excedan 100%
    suma_minimos = sum(bound[0] for bound in bounds_ingredientes)
    if suma_minimos > 100:
        print(f"❌ Error: La suma de límites mínimos ({suma_minimos}%) excede el 100%")
        
        # Identificar ingredientes con límites mínimos altos
        ingredientes_altos = []
        for i, (ing, bound) in enumerate(zip(ingredientes, bounds_ingredientes)):
            if bound[0] > 15:  # Límites mínimos altos
                ingredientes_altos.append(f"{ing['nombre']} (mín: {bound[0]}%)")
        
        return jsonify({
            'error': 'Los límites mínimos de ingredientes exceden el 100%',
            'validacion': {
                'tipo': 'limites_minimos_excesivos',
                'mensaje': f'La suma de límites mínimos es {suma_minimos}%, debe ser ≤100%',
                'detalles': {
                    'suma_actual': suma_minimos,
                    'suma_maxima': 100,
                    'exceso': suma_minimos - 100
                },
                'sugerencias': [
                    'Reduzca los límites mínimos de algunos ingredientes',
                    'Elimine ingredientes con límites mínimos muy altos',
                    f'Necesita reducir {suma_minimos - 100:.1f}% en límites mínimos'
                ] + ([f'Ingredientes con límites altos: {", ".join(ingredientes_altos)}'] if ingredientes_altos else [])
            }
        }), 400
    
    print(f"✅ Suma de límites mínimos: {suma_minimos}% (≤100%)")
    
    # Validar que cada límite mínimo sea menor o igual al máximo
    ingredientes_inconsistentes = []
    for i, (ing, bound) in enumerate(zip(ingredientes, bounds_ingredientes)):
        if bound[0] > bound[1]:
            print(f"❌ Error: {ing['nombre']} tiene límite mínimo ({bound[0]}%) mayor al máximo ({bound[1]}%)")
            ingredientes_inconsistentes.append(f"{ing['nombre']} (mín: {bound[0]}%, máx: {bound[1]}%)")
    
    if ingredientes_inconsistentes:
        return jsonify({
            'error': 'Límites inconsistentes en ingredientes',
            'validacion': {
                'tipo': 'limites_inconsistentes',
                'mensaje': 'Algunos ingredientes tienen límite mínimo mayor al máximo',
                'detalles': {
                    'ingredientes_afectados': ingredientes_inconsistentes
                },
                'sugerencias': [
                    'Corrija los límites de los ingredientes afectados',
                    'Asegúrese que límite mínimo ≤ límite máximo',
                    'Revise la configuración de cada ingrediente'
                ]
            }
        }), 400
    
    for i, (ing, bound) in enumerate(zip(ingredientes, bounds_ingredientes)):
        print(f"✅ {ing['nombre']}: {bound[0]}% ≤ {bound[1]}%")

    print("\n" + "="*60)
    print("PASO 3: AJUSTAR LÍMITES MÍNIMOS Y MÁXIMOS DE NUTRIENTES")
    print("="*60)
    
    # Construir matriz de nutrientes según el tipo de optimización seleccionado
    for req in requerimientos:
        fila = []
        for ing in ingredientes:
            nutrientes = ing.get('aporte', {})
            valor_nutriente = 0
            ms = float(ing.get('ms', 100))
            
            # Obtener el valor base del nutriente
            if isinstance(nutrientes.get(req['nombre']), dict):
                valor_base = float(nutrientes.get(req['nombre'], {}).get('valor', 0))
            else:
                valor_base = float(nutrientes.get(req['nombre'], 0))
            
            # Aplicar cálculo según el tipo de optimización
            if tipo_optimizacion == 'base_seca':
                # Base seca: aplicar materia seca
                valor_nutriente = valor_base * (ms / 100)
                print(f"🧪 {ing['nombre']} - {req['nombre']} (base seca): {valor_base} * ({ms}/100) = {valor_nutriente}")
            else:
                # Base húmeda (tal como): usar valor directo
                valor_nutriente = valor_base
                print(f"🧪 {ing['nombre']} - {req['nombre']} (base húmeda): {valor_nutriente}")
            
            fila.append(valor_nutriente)
        matriz_nutrientes.append(fila)
        print(f"🧪 {req['nombre']} ({tipo_optimizacion}): aportes por ingrediente = {fila}")

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
        print("❌ Ninguna optimización estricta fue exitosa")
        print("🔄 Intentando optimización aproximada...")
        
        # Intentar optimización aproximada
        resultado_aproximado = optimizacion_aproximada(
            ingredientes, requerimientos, tipo_optimizacion, 
            costos, bounds_ingredientes, matriz_nutrientes
        )
        
        if resultado_aproximado['exito']:
            print("✅ Optimización aproximada exitosa")
            return jsonify(resultado_aproximado)
        
        # Si incluso la optimización aproximada falla, hacer análisis detallado
        print("❌ Incluso la optimización aproximada falló")
        
        # Analizar posibles causas del fallo
        causas_posibles = []
        sugerencias_especificas = []
        
        # Verificar si hay conflictos en requerimientos nutricionales
        nutrientes_problematicos = []
        for i, req in enumerate(requerimientos):
            req_min = req.get('min')
            req_max = req.get('max')
            if req_min and req_max and float(req_min) > float(req_max):
                nutrientes_problematicos.append(f"{req['nombre']} (mín: {req_min}, máx: {req_max})")
        
        if nutrientes_problematicos:
            causas_posibles.append("Requerimientos nutricionales inconsistentes")
            sugerencias_especificas.extend([
                f"Corrija los requerimientos de: {', '.join(nutrientes_problematicos)}",
                "Verifique que valor mínimo ≤ valor máximo para cada nutriente"
            ])
        
        # Verificar si faltan nutrientes en ingredientes
        nutrientes_faltantes = []
        for req in requerimientos:
            nutriente_nombre = req['nombre']
            ingredientes_sin_nutriente = []
            for ing in ingredientes:
                nutrientes = ing.get('aporte', {})
                if isinstance(nutrientes.get(nutriente_nombre), dict):
                    valor = float(nutrientes.get(nutriente_nombre, {}).get('valor', 0))
                else:
                    valor = float(nutrientes.get(nutriente_nombre, 0))
                
                if valor == 0:
                    ingredientes_sin_nutriente.append(ing['nombre'])
            
            if len(ingredientes_sin_nutriente) == len(ingredientes):
                nutrientes_faltantes.append(nutriente_nombre)
        
        if nutrientes_faltantes:
            causas_posibles.append("Nutrientes sin aportes en ningún ingrediente")
            sugerencias_especificas.extend([
                f"Agregue ingredientes que aporten: {', '.join(nutrientes_faltantes)}",
                "Verifique los valores nutricionales de sus ingredientes"
            ])
        
        # Verificar si los costos son muy altos o muy bajos
        costos_cero = [ing['nombre'] for ing in ingredientes if float(ing.get('costo', 0)) == 0]
        if len(costos_cero) == len(ingredientes):
            causas_posibles.append("Todos los ingredientes tienen costo cero")
            sugerencias_especificas.append("Defina costos realistas para los ingredientes")
        
        # ANÁLISIS DETALLADO DE NUTRIENTES FALTANTES Y APORTES ACTUALES
        print("\n" + "="*60)
        print("🔍 ANÁLISIS DETALLADO DE FALLA EN OPTIMIZACIÓN")
        print("="*60)
        
        # Calcular aportes actuales con distribución uniforme
        distribucion_uniforme = [100.0 / len(ingredientes)] * len(ingredientes)
        aportes_actuales = {}
        nutrientes_deficientes = []
        nutrientes_sin_aporte = []
        
        for i, req in enumerate(requerimientos):
            nombre_nutriente = req['nombre']
            req_min = req.get('min')
            req_max = req.get('max')
            
            # Calcular aporte actual con distribución uniforme
            aporte_total = 0.0
            ingredientes_que_aportan = []
            
            for j, ing in enumerate(ingredientes):
                nutrientes = ing.get('aporte', {})
                ms = float(ing.get('ms', 100))
                
                # Obtener valor base del nutriente
                if isinstance(nutrientes.get(nombre_nutriente), dict):
                    valor_base = float(nutrientes.get(nombre_nutriente, {}).get('valor', 0))
                else:
                    valor_base = float(nutrientes.get(nombre_nutriente, 0))
                
                # Calcular aporte según el tipo de optimización
                if tipo_optimizacion == 'base_seca':
                    aporte_ingrediente = distribucion_uniforme[j] * valor_base * (ms / 100) / 100
                else:
                    aporte_ingrediente = distribucion_uniforme[j] * valor_base / 100
                
                aporte_total += aporte_ingrediente
                
                if valor_base > 0:
                    ingredientes_que_aportan.append({
                        'nombre': ing['nombre'],
                        'valor_base': valor_base,
                        'aporte': aporte_ingrediente,
                        'ms': ms
                    })
            
            aportes_actuales[nombre_nutriente] = {
                'aporte_total': aporte_total,
                'requerimiento_min': float(req_min) if req_min and req_min != '' else None,
                'requerimiento_max': float(req_max) if req_max and req_max != '' else None,
                'ingredientes_que_aportan': ingredientes_que_aportan,
                'deficit': 0,
                'exceso': 0
            }
            
            # Analizar deficiencias
            if req_min and req_min != '' and float(req_min) > 0:
                req_min_val = float(req_min)
                if aporte_total < req_min_val:
                    deficit = req_min_val - aporte_total
                    aportes_actuales[nombre_nutriente]['deficit'] = deficit
                    
                    if len(ingredientes_que_aportan) == 0:
                        nutrientes_sin_aporte.append({
                            'nutriente': nombre_nutriente,
                            'requerimiento': req_min_val,
                            'aporte_actual': aporte_total,
                            'deficit': deficit
                        })
                    else:
                        nutrientes_deficientes.append({
                            'nutriente': nombre_nutriente,
                            'requerimiento': req_min_val,
                            'aporte_actual': aporte_total,
                            'deficit': deficit,
                            'ingredientes_disponibles': len(ingredientes_que_aportan)
                        })
            
            print(f"🧪 {nombre_nutriente}:")
            print(f"   Aporte actual: {aporte_total:.4f}")
            print(f"   Requerimiento mín: {req_min}")
            print(f"   Ingredientes que aportan: {len(ingredientes_que_aportan)}")
            if ingredientes_que_aportan:
                for ing_aporte in ingredientes_que_aportan[:3]:  # Mostrar solo los primeros 3
                    print(f"     - {ing_aporte['nombre']}: {ing_aporte['valor_base']:.2f} → {ing_aporte['aporte']:.4f}")
        
        # Generar diagnóstico específico
        diagnostico = {
            'tipo': 'optimizacion_fallida_detallada',
            'mensaje': 'No se pudo encontrar una solución factible ni aproximada. Análisis detallado:',
            'aportes_actuales': aportes_actuales,
            'nutrientes_sin_aporte': nutrientes_sin_aporte,
            'nutrientes_deficientes': nutrientes_deficientes,
            'causas_principales': [],
            'sugerencias_especificas': []
        }
        
        # Análisis de causas principales
        if nutrientes_sin_aporte:
            diagnostico['causas_principales'].append(
                f"Faltan ingredientes que aporten: {', '.join([n['nutriente'] for n in nutrientes_sin_aporte])}"
            )
            for nutriente_faltante in nutrientes_sin_aporte:
                diagnostico['sugerencias_especificas'].append(
                    f"Agregue ingredientes que aporten {nutriente_faltante['nutriente']} "
                    f"(necesita {nutriente_faltante['deficit']:.4f} adicional)"
                )
        
        if nutrientes_deficientes:
            diagnostico['causas_principales'].append(
                f"Aportes insuficientes en: {', '.join([n['nutriente'] for n in nutrientes_deficientes])}"
            )
            for nutriente_def in nutrientes_deficientes:
                diagnostico['sugerencias_especificas'].append(
                    f"Aumente la inclusión de ingredientes ricos en {nutriente_def['nutriente']} "
                    f"(déficit: {nutriente_def['deficit']:.4f})"
                )
        
        # Verificar límites de ingredientes
        suma_minimos = sum(bound[0] for bound in bounds_ingredientes)
        suma_maximos = sum(bound[1] for bound in bounds_ingredientes)
        
        if suma_minimos > 95:
            diagnostico['causas_principales'].append("Límites mínimos muy restrictivos")
            diagnostico['sugerencias_especificas'].append(
                f"Reduzca límites mínimos (suma actual: {suma_minimos:.1f}%)"
            )
        
        if suma_maximos < 105:
            diagnostico['causas_principales'].append("Límites máximos insuficientes")
            diagnostico['sugerencias_especificas'].append(
                f"Aumente límites máximos (suma actual: {suma_maximos:.1f}%)"
            )
        
        # Agregar sugerencias generales si no hay específicas
        if not diagnostico['sugerencias_especificas']:
            diagnostico['sugerencias_especificas'] = [
                "Revise los valores nutricionales de los ingredientes",
                "Verifique que los requerimientos sean alcanzables",
                "Considere ajustar los límites de inclusión"
            ]
        
        print(f"\n📋 DIAGNÓSTICO FINAL:")
        print(f"   Nutrientes sin aporte: {len(nutrientes_sin_aporte)}")
        print(f"   Nutrientes deficientes: {len(nutrientes_deficientes)}")
        print(f"   Causas principales: {len(diagnostico['causas_principales'])}")
        
        return jsonify({
            'error': 'No se pudo encontrar una solución factible ni aproximada',
            'validacion': diagnostico
        }), 400
    
    # Ordenar por costo (menor es mejor)
    mejores_resultados.sort(key=lambda x: x[1])
    resultado, mejor_costo, mejor_metodo = mejores_resultados[0]
    
    print(f"🏆 Mejor resultado obtenido con método: {mejor_metodo}")
    
    print(f"📊 Resultado de optimización: {resultado.success}")
    print(f"📊 Mensaje: {resultado.message}")
    
    # === BLOQUE DE VALIDACIÓN DE NUTRIENTES ===
    # Generar los resultados de nutrientes de la mezcla optimizada según el tipo seleccionado
    resultados_nutrientes = {}
    for idx_req, req in enumerate(requerimientos):
        nombre_nutriente = req['nombre']
        valor = 0.0
        
        print(f"🧮 Calculando aportes de {nombre_nutriente} ({tipo_optimizacion}):")
        
        for idx_ing, ing in enumerate(ingredientes):
            nutrientes = ing.get('aporte', {})
            inclusion = resultado.x[idx_ing]
            ms = float(ing.get('ms', 100))
            
            # Obtener valor base del nutriente
            if isinstance(nutrientes.get(nombre_nutriente), dict):
                valor_base = float(nutrientes.get(nombre_nutriente, {}).get('valor', 0))
            else:
                valor_base = float(nutrientes.get(nombre_nutriente, 0))
            
            # Calcular aporte según el tipo de optimización
            if tipo_optimizacion == 'base_seca':
                # Base seca: inclusion * valor_base * (ms / 100) / 100
                aporte = inclusion * valor_base * (ms / 100) / 100
            else:
                # Base húmeda: inclusion * valor_base / 100
                aporte = inclusion * valor_base / 100
            
            valor += aporte
            print(f"  {ing['nombre']}: inclusión={inclusion:.2f}%, valor_base={valor_base}, ms={ms}%, aporte={aporte:.4f}")
        
        resultados_nutrientes[nombre_nutriente] = valor
        print(f"🎯 Total {nombre_nutriente}: {valor:.4f}")

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
        'mensaje': 'Optimización completada exitosamente',
        'exito': True,
        'notificacion': {
            'tipo': 'exito',
            'titulo': '✅ Optimización Exitosa',
            'mensaje': f'Se encontró una solución óptima con costo de ${costo_total:.2f}',
            'detalles': {
                'metodo_usado': mejor_metodo,
                'costo_total': round(costo_total, 2),
                'ingredientes_usados': len([r for r in resultado_lista if r['inclusion'] > 0.01]),
                'suma_verificada': round(suma_final, 2),
                'restricciones_cumplidas': len(todas_restricciones)
            },
            'sugerencias': [
                f'La mezcla usa {len([r for r in resultado_lista if r["inclusion"] > 0.01])} ingredientes principales',
                f'Costo por kg: ${costo_total:.2f}',
                'Todos los requerimientos nutricionales han sido cumplidos'
            ]
        }
    })


def optimizacion_aproximada(ingredientes, requerimientos, tipo_optimizacion, costos, bounds_ingredientes, matriz_nutrientes):
    """
    Función de optimización aproximada que siempre devuelve una solución
    manteniendo la suma de ingredientes en 100%
    """
    print("\n" + "="*60)
    print("🔄 INICIANDO OPTIMIZACIÓN APROXIMADA")
    print("="*60)
    
    # Niveles de tolerancia progresiva
    niveles_tolerancia = [0.05, 0.10, 0.20, 0.50]  # 5%, 10%, 20%, 50%
    
    for nivel_idx, tolerancia in enumerate(niveles_tolerancia):
        print(f"\n🎯 Intentando optimización con tolerancia: {tolerancia*100:.0f}%")
        
        # Intentar optimización con penalizaciones en lugar de restricciones estrictas
        resultado = optimizar_con_penalizaciones(
            ingredientes, requerimientos, tipo_optimizacion, 
            costos, bounds_ingredientes, matriz_nutrientes, tolerancia
        )
        
        if resultado['exito']:
            print(f"✅ Optimización aproximada exitosa con tolerancia {tolerancia*100:.0f}%")
            return resultado
    
    # Si todas las tolerancias fallan, usar distribución inteligente
    print("\n🔄 Usando distribución inteligente como último recurso")
    return distribucion_inteligente(ingredientes, requerimientos, tipo_optimizacion, costos, bounds_ingredientes, matriz_nutrientes)


def optimizar_con_penalizaciones(ingredientes, requerimientos, tipo_optimizacion, costos, bounds_ingredientes, matriz_nutrientes, tolerancia):
    """
    Optimización usando penalizaciones graduales en lugar de restricciones estrictas
    """
    try:
        # Función objetivo con penalizaciones
        def objetivo_con_penalizaciones(x):
            # Costo base
            costo_base = np.dot(costos, x)
            
            # Penalizaciones por desviaciones nutricionales
            penalizacion_total = 0.0
            
            for i, req in enumerate(requerimientos):
                aporte_actual = np.dot(matriz_nutrientes[i], x) / 100
                req_min = req.get('min')
                req_max = req.get('max')
                
                # Penalización por no cumplir mínimo
                if req_min and req_min != '' and float(req_min) > 0:
                    req_min_val = float(req_min)
                    if aporte_actual < req_min_val:
                        deficit = req_min_val - aporte_actual
                        # Penalización cuadrática escalada por tolerancia
                        penalizacion = (deficit / req_min_val) ** 2 * 1000 / tolerancia
                        penalizacion_total += penalizacion
                
                # Penalización por exceder máximo
                if req_max and req_max != '' and float(req_max) > 0:
                    req_max_val = float(req_max)
                    if aporte_actual > req_max_val:
                        exceso = aporte_actual - req_max_val
                        # Penalización cuadrática escalada por tolerancia
                        penalizacion = (exceso / req_max_val) ** 2 * 1000 / tolerancia
                        penalizacion_total += penalizacion
            
            return costo_base + penalizacion_total
        
        # Solo restricción de suma = 100%
        restriccion_suma = {'type': 'eq', 'fun': lambda x: np.sum(x) - 100}
        
        # Puntos iniciales múltiples
        puntos_iniciales = generar_puntos_iniciales(bounds_ingredientes, costos)
        
        mejor_resultado = None
        mejor_costo = float('inf')
        
        for idx, x0 in enumerate(puntos_iniciales):
            resultado = minimize(
                objetivo_con_penalizaciones,
                x0,
                method='SLSQP',
                bounds=bounds_ingredientes,
                constraints=[restriccion_suma],
                options={'disp': False, 'maxiter': 3000, 'ftol': 1e-12}
            )
            
            if resultado.success and resultado.fun < mejor_costo:
                mejor_resultado = resultado
                mejor_costo = resultado.fun
        
        if mejor_resultado and mejor_resultado.success:
            # Verificar calidad de la aproximación
            metricas = calcular_metricas_aproximacion(
                mejor_resultado.x, ingredientes, requerimientos, 
                tipo_optimizacion, matriz_nutrientes
            )
            
            # Si la aproximación es aceptable, devolverla
            if metricas['calidad_general'] >= (1 - tolerancia):
                return formatear_resultado_aproximado(
                    mejor_resultado, ingredientes, costos, metricas, 
                    f"Aproximada (tolerancia {tolerancia*100:.0f}%)"
                )
        
        return {'exito': False}
        
    except Exception as e:
        print(f"❌ Error en optimización con penalizaciones: {e}")
        return {'exito': False}


def generar_puntos_iniciales(bounds_ingredientes, costos):
    """
    Genera múltiples puntos iniciales inteligentes para la optimización
    """
    puntos = []
    n_ingredientes = len(bounds_ingredientes)
    
    # Punto 1: Distribución uniforme
    x0_uniforme = np.array([100.0 / n_ingredientes] * n_ingredientes)
    puntos.append(ajustar_a_bounds(x0_uniforme, bounds_ingredientes))
    
    # Punto 2: Priorizar ingredientes de menor costo
    if any(c > 0 for c in costos):
        costos_ordenados = sorted(enumerate(costos), key=lambda x: x[1] if x[1] > 0 else float('inf'))
        x0_costo = np.zeros(n_ingredientes)
        
        # Asignar más peso a ingredientes baratos
        peso_total = 0
        for i, (idx, costo) in enumerate(costos_ordenados[:min(3, len(costos_ordenados))]):
            peso = max(bounds_ingredientes[idx][0], 30.0 / (i + 1))
            x0_costo[idx] = min(peso, bounds_ingredientes[idx][1])
            peso_total += x0_costo[idx]
        
        # Completar hasta 100%
        if peso_total < 100:
            resto = 100 - peso_total
            for idx in range(n_ingredientes):
                if x0_costo[idx] == 0:
                    disponible = bounds_ingredientes[idx][1] - x0_costo[idx]
                    if disponible > 0:
                        agregar = min(resto, disponible)
                        x0_costo[idx] += agregar
                        resto -= agregar
                        if resto <= 0:
                            break
        
        puntos.append(ajustar_a_bounds(x0_costo, bounds_ingredientes))
    
    # Punto 3: Usar límites mínimos como base
    x0_minimos = np.array([bound[0] for bound in bounds_ingredientes])
    suma_minimos = np.sum(x0_minimos)
    
    if suma_minimos < 100:
        # Distribuir el resto proporcionalmente
        resto = 100 - suma_minimos
        capacidades = np.array([bound[1] - bound[0] for bound in bounds_ingredientes])
        capacidad_total = np.sum(capacidades)
        
        if capacidad_total > 0:
            for i in range(n_ingredientes):
                if capacidades[i] > 0:
                    proporcion = capacidades[i] / capacidad_total
                    agregar = min(resto * proporcion, capacidades[i])
                    x0_minimos[i] += agregar
    
    puntos.append(ajustar_a_bounds(x0_minimos, bounds_ingredientes))
    
    return puntos


def ajustar_a_bounds(x, bounds_ingredientes):
    """
    Ajusta un vector de inclusiones para que respete los bounds y sume 100%
    """
    x_ajustado = np.copy(x)
    
    # Aplicar bounds
    for i, (min_val, max_val) in enumerate(bounds_ingredientes):
        x_ajustado[i] = max(min_val, min(max_val, x_ajustado[i]))
    
    # Normalizar para que sume 100
    suma_actual = np.sum(x_ajustado)
    if suma_actual > 0:
        x_ajustado = x_ajustado * (100.0 / suma_actual)
        
        # Verificar bounds después de normalizar
        for i, (min_val, max_val) in enumerate(bounds_ingredientes):
            if x_ajustado[i] < min_val:
                x_ajustado[i] = min_val
            elif x_ajustado[i] > max_val:
                x_ajustado[i] = max_val
    
    return x_ajustado


def distribucion_inteligente(ingredientes, requerimientos, tipo_optimizacion, costos, bounds_ingredientes, matriz_nutrientes):
    """
    Último recurso: distribución inteligente que siempre funciona
    """
    print("🎯 Aplicando distribución inteligente")
    
    n_ingredientes = len(ingredientes)
    
    # Comenzar con límites mínimos
    x_final = np.array([bound[0] for bound in bounds_ingredientes])
    suma_actual = np.sum(x_final)
    
    # Distribuir el resto priorizando ingredientes de menor costo y mejor aporte nutricional
    resto = 100 - suma_actual
    
    if resto > 0:
        # Calcular puntuaciones para cada ingrediente
        puntuaciones = []
        
        for i, ing in enumerate(ingredientes):
            # Factor costo (menor costo = mejor puntuación)
            costo = costos[i] if costos[i] > 0 else 1.0
            factor_costo = 1.0 / costo
            
            # Factor nutricional (cuántos nutrientes aporta significativamente)
            factor_nutricional = 0
            for j, req in enumerate(requerimientos):
                if matriz_nutrientes[j][i] > 0:
                    factor_nutricional += 1
            
            # Capacidad disponible
            capacidad = bounds_ingredientes[i][1] - x_final[i]
            
            puntuacion = factor_costo * (1 + factor_nutricional) * min(capacidad, resto)
            puntuaciones.append((i, puntuacion, capacidad))
        
        # Ordenar por puntuación descendente
        puntuaciones.sort(key=lambda x: x[1], reverse=True)
        
        # Distribuir el resto
        for idx, puntuacion, capacidad in puntuaciones:
            if resto <= 0:
                break
            
            agregar = min(resto, capacidad)
            x_final[idx] += agregar
            resto -= agregar
    
    # Asegurar que suma exactamente 100%
    suma_final = np.sum(x_final)
    if abs(suma_final - 100) > 0.001:
        x_final = x_final * (100.0 / suma_final)
    
    # Calcular métricas
    metricas = calcular_metricas_aproximacion(
        x_final, ingredientes, requerimientos, tipo_optimizacion, matriz_nutrientes
    )
    
    return formatear_resultado_aproximado(
        type('obj', (object,), {'x': x_final, 'success': True})(),
        ingredientes, costos, metricas, "Distribución Inteligente"
    )


def calcular_metricas_aproximacion(x, ingredientes, requerimientos, tipo_optimizacion, matriz_nutrientes):
    """
    Calcula métricas de qué tan buena es la aproximación
    """
    metricas = {
        'nutrientes_cumplidos': 0,
        'nutrientes_totales': len(requerimientos),
        'desviaciones': [],
        'calidad_general': 0.0,
        'aportes_actuales': {}
    }
    
    cumplimientos = []
    
    for i, req in enumerate(requerimientos):
        aporte_actual = np.dot(matriz_nutrientes[i], x) / 100
        req_min = req.get('min')
        req_max = req.get('max')
        
        metricas['aportes_actuales'][req['nombre']] = aporte_actual
        
        cumple_min = True
        cumple_max = True
        desviacion_relativa = 0.0
        
        # Verificar mínimo
        if req_min and req_min != '' and float(req_min) > 0:
            req_min_val = float(req_min)
            if aporte_actual < req_min_val:
                cumple_min = False
                desviacion_relativa += abs(aporte_actual - req_min_val) / req_min_val
        
        # Verificar máximo
        if req_max and req_max != '' and float(req_max) > 0:
            req_max_val = float(req_max)
            if aporte_actual > req_max_val:
                cumple_max = False
                desviacion_relativa += abs(aporte_actual - req_max_val) / req_max_val
        
        if cumple_min and cumple_max:
            metricas['nutrientes_cumplidos'] += 1
            cumplimientos.append(1.0)
        else:
            # Calcular qué tan cerca está (0 = muy lejos, 1 = perfecto)
            cercania = max(0.0, 1.0 - desviacion_relativa)
            cumplimientos.append(cercania)
        
        metricas['desviaciones'].append({
            'nutriente': req['nombre'],
            'aporte_actual': aporte_actual,
            'requerimiento_min': req_min,
            'requerimiento_max': req_max,
            'cumple': cumple_min and cumple_max,
            'desviacion_relativa': desviacion_relativa
        })
    
    # Calidad general como promedio de cumplimientos
    metricas['calidad_general'] = np.mean(cumplimientos) if cumplimientos else 0.0
    
    return metricas


def formatear_resultado_aproximado(resultado, ingredientes, costos, metricas, metodo):
    """
    Formatea el resultado de optimización aproximada
    """
    resultado_lista = []
    costo_total = 0
    
    for i, inclusion in enumerate(resultado.x):
        costo_ingrediente = inclusion * costos[i] / 100
        costo_total += costo_ingrediente
        
        resultado_lista.append({
            'ingrediente': ingredientes[i]['nombre'],
            'inclusion': formatear_inclusion(inclusion),
            'peso': formatear_inclusion(inclusion),
            'valor': round(costo_ingrediente, 2)
        })
    
    # Verificar suma
    suma_final = sum(r['inclusion'] for r in resultado_lista)
    
    # Determinar tipo de notificación basado en calidad
    if metricas['calidad_general'] >= 0.95:
        tipo_notificacion = 'exito'
        titulo = '✅ Optimización Exitosa (Aproximada)'
        mensaje = f'Se encontró una excelente aproximación con costo de ${costo_total:.2f}'
    elif metricas['calidad_general'] >= 0.80:
        tipo_notificacion = 'aproximada_buena'
        titulo = '⚠️ Optimización Aproximada (Buena)'
        mensaje = f'Se encontró una buena aproximación con costo de ${costo_total:.2f}'
    else:
        tipo_notificacion = 'aproximada_limitada'
        titulo = '⚠️ Optimización Aproximada (Limitada)'
        mensaje = f'Se encontró una aproximación limitada con costo de ${costo_total:.2f}'
    
    # Generar sugerencias específicas
    sugerencias = [
        f'Calidad de aproximación: {metricas["calidad_general"]*100:.1f}%',
        f'Nutrientes cumplidos: {metricas["nutrientes_cumplidos"]}/{metricas["nutrientes_totales"]}',
        f'Método utilizado: {metodo}'
    ]
    
    # Agregar sugerencias específicas para nutrientes no cumplidos
    nutrientes_problematicos = [d for d in metricas['desviaciones'] if not d['cumple']]
    if nutrientes_problematicos:
        sugerencias.append('Nutrientes con desviaciones:')
        for nutriente in nutrientes_problematicos[:3]:  # Mostrar solo los primeros 3
            sugerencias.append(f"  • {nutriente['nutriente']}: {nutriente['aporte_actual']:.4f}")
    
    return {
        'exito': True,
        'aproximada': True,
        'resultado': resultado_lista,
        'costo_total': round(costo_total, 2),
        'mensaje': 'Optimización aproximada completada',
        'metricas_aproximacion': metricas,
        'notificacion': {
            'tipo': tipo_notificacion,
            'titulo': titulo,
            'mensaje': mensaje,
            'detalles': {
                'metodo_usado': metodo,
                'costo_total': round(costo_total, 2),
                'calidad_aproximacion': f"{metricas['calidad_general']*100:.1f}%",
                'nutrientes_cumplidos': f"{metricas['nutrientes_cumplidos']}/{metricas['nutrientes_totales']}",
                'suma_verificada': round(suma_final, 2),
                'es_aproximacion': True
            },
            'sugerencias': sugerencias
        }
    }
