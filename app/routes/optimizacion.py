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

    # Obtener todos los ingredientes con límites
    # Verificar si las columnas de límites existen
    cursor.execute("""
        SELECT COLUMN_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = DATABASE() 
        AND TABLE_NAME = 'ingredientes'
        AND COLUMN_NAME IN ('limite_min', 'limite_max')
    """)
    columnas_limites = cursor.fetchall()
    tiene_limites = len(columnas_limites) == 2
    
    if tiene_limites:
        cursor.execute("""
            SELECT id, nombre, comentario, ms, precio, 
                   COALESCE(limite_min, 0.00) as limite_min,
                   COALESCE(limite_max, 100.00) as limite_max
            FROM ingredientes 
            WHERE usuario_id = %s 
            ORDER BY nombre ASC
        """, (session['user_id'],))
    else:
        cursor.execute("""
            SELECT id, nombre, comentario, ms, precio,
                   0.00 as limite_min,
                   100.00 as limite_max
            FROM ingredientes 
            WHERE usuario_id = %s 
            ORDER BY nombre ASC
        """, (session['user_id'],))
    
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
            'limite_min': float(ing_typed.get('limite_min', 0.0)) if hasattr(ing_typed, 'get') else 0.0,
            'limite_max': float(ing_typed.get('limite_max', 100.0)) if hasattr(ing_typed, 'get') else 100.0,
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

def diagnosticar_fallo_optimizacion(ingredientes, requerimientos, bounds_ingredientes, matriz_nutrientes):
    """
    Diagnostica por qué falló la optimización y devuelve un mensaje explicativo detallado
    """
    diagnosticos = []
    
    # 1. Verificar límites de ingredientes
    suma_minimos = sum(bound[0] for bound in bounds_ingredientes)
    suma_maximos = sum(bound[1] for bound in bounds_ingredientes)
    
    if suma_minimos > 100:
        diagnosticos.append({
            'tipo': 'limites_incompatibles',
            'titulo': 'Límites mínimos incompatibles',
            'mensaje': f'La suma de los límites mínimos de ingredientes es {suma_minimos:.1f}%, pero debe ser ≤ 100%.',
            'solucion': 'Reduce los límites mínimos de algunos ingredientes para que su suma no exceda el 100%.',
            'detalles': [f"{ing['nombre']}: mín {bound[0]}%" for ing, bound in zip(ingredientes, bounds_ingredientes) if bound[0] > 0]
        })
    
    if suma_maximos < 100:
        diagnosticos.append({
            'tipo': 'limites_incompatibles',
            'titulo': 'Límites máximos insuficientes',
            'mensaje': f'La suma de los límites máximos de ingredientes es {suma_maximos:.1f}%, pero debe ser ≥ 100%.',
            'solucion': 'Aumenta los límites máximos de algunos ingredientes para permitir mezclas que sumen 100%.',
            'detalles': [f"{ing['nombre']}: máx {bound[1]}%" for ing, bound in zip(ingredientes, bounds_ingredientes)]
        })
    
    # 2. Verificar límites individuales de ingredientes
    for ing, bound in zip(ingredientes, bounds_ingredientes):
        if bound[0] > bound[1]:
            diagnosticos.append({
                'tipo': 'limite_individual_invalido',
                'titulo': f'Límite inválido en {ing["nombre"]}',
                'mensaje': f'El límite mínimo ({bound[0]}%) es mayor al máximo ({bound[1]}%).',
                'solucion': f'Ajusta los límites de {ing["nombre"]} para que mínimo ≤ máximo.',
                'detalles': []
            })
    
    # 3. Verificar disponibilidad de nutrientes
    for i, req in enumerate(requerimientos):
        req_min = req.get('min')
        if req_min and float(req_min) > 0:
            # Calcular el máximo aporte posible de este nutriente
            max_aporte_posible = 0
            for j, ing in enumerate(ingredientes):
                max_inclusion = bounds_ingredientes[j][1]
                aporte_nutriente = matriz_nutrientes[i][j]
                max_aporte_posible += (max_inclusion * aporte_nutriente) / 100
            
            if max_aporte_posible < float(req_min):
                diagnosticos.append({
                    'tipo': 'nutriente_insuficiente',
                    'titulo': f'Nutriente {req["nombre"]} insuficiente',
                    'mensaje': f'El máximo aporte posible de {req["nombre"]} es {max_aporte_posible:.3f}, pero se requiere mínimo {req_min}.',
                    'solucion': f'Agrega ingredientes con mayor contenido de {req["nombre"]} o reduce el requerimiento mínimo.',
                    'detalles': [f"{ing['nombre']}: {matriz_nutrientes[i][j]:.3f} por 100%" for j, ing in enumerate(ingredientes) if matriz_nutrientes[i][j] > 0]
                })
    
    # 4. Verificar costos
    costos_cero = [ing['nombre'] for ing in ingredientes if float(ing.get('costo', 0)) == 0]
    if len(costos_cero) == len(ingredientes):
        diagnosticos.append({
            'tipo': 'costos_faltantes',
            'titulo': 'Costos no definidos',
            'mensaje': 'Todos los ingredientes tienen costo $0, lo que puede causar problemas en la optimización.',
            'solucion': 'Define costos realistas para los ingredientes.',
            'detalles': costos_cero
        })
    
    # 5. Verificar datos de nutrientes
    ingredientes_sin_nutrientes = []
    for ing in ingredientes:
        aporte = ing.get('aporte', {})
        if not aporte or all(float(v) == 0 for v in aporte.values()):
            ingredientes_sin_nutrientes.append(ing['nombre'])
    
    if ingredientes_sin_nutrientes:
        diagnosticos.append({
            'tipo': 'nutrientes_faltantes',
            'titulo': 'Ingredientes sin información nutricional',
            'mensaje': f'{len(ingredientes_sin_nutrientes)} ingrediente(s) no tienen datos de nutrientes.',
            'solucion': 'Completa la información nutricional de todos los ingredientes.',
            'detalles': ingredientes_sin_nutrientes
        })
    
    return diagnosticos

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
            'diagnostico': {
                'tipo': 'datos_incompletos',
                'titulo': 'Datos insuficientes para optimizar',
                'mensaje': 'Se necesitan al menos un ingrediente y un requerimiento nutricional.',
                'solucion': 'Agrega ingredientes y define requerimientos nutricionales antes de optimizar.',
                'detalles': []
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
        # Usar precio en lugar de costo
        precio = float(ing.get('precio', 0))
        costos.append(precio)
        
        # Obtener límites del ingrediente (ya incluidos en la consulta)
        limite_min = float(ing.get('limite_min', 0))
        limite_max = float(ing.get('limite_max', 100))
        
        # Debug: mostrar datos recibidos
        print(f"🔍 Datos ingrediente {ing['nombre']}:")
        print(f"   - limite_min: {limite_min}")
        print(f"   - limite_max: {limite_max}")
        print(f"   - precio: {precio}")
        
        # Validar límites
        if limite_min < 0:
            limite_min = 0
        if limite_max > 100:
            limite_max = 100
        if limite_min > limite_max:
            limite_min = 0
            limite_max = 100
        
        bounds_ingredientes.append((limite_min, limite_max))
        
        print(f"📊 {ing['nombre']}: bounds=({bounds_ingredientes[-1][0]}, {bounds_ingredientes[-1][1]}), precio={precio}")

    # Construir matriz de nutrientes para diagnóstico temprano
    matriz_nutrientes = []
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
                valor_nutriente = valor_base * (ms / 100)
            else:
                valor_nutriente = valor_base
            
            fila.append(valor_nutriente)
        matriz_nutrientes.append(fila)

    # Realizar diagnóstico temprano
    diagnosticos_tempranos = diagnosticar_fallo_optimizacion(ingredientes, requerimientos, bounds_ingredientes, matriz_nutrientes)
    
    if diagnosticos_tempranos:
        print("❌ Errores detectados en validación temprana:")
        for diag in diagnosticos_tempranos:
            print(f"   - {diag['titulo']}: {diag['mensaje']}")
        
        return jsonify({
            'error': 'Problemas detectados antes de la optimización',
            'diagnosticos': diagnosticos_tempranos
        }), 400

    print(f"✅ Validaciones tempranas completadas exitosamente")

    print("\n" + "="*60)
    print("PASO 2: VALIDAR LÍMITES MÍNIMOS Y MÁXIMOS DE INGREDIENTES")
    print("="*60)
    
    # Verificar que la suma de límites máximos permita llegar a 100%
    suma_maximos = sum(bound[1] for bound in bounds_ingredientes)
    print(f"✅ Suma de límites máximos: {suma_maximos}% (≥100%)")
    
    # Verificar que los límites mínimos no excedan 100%
    suma_minimos = sum(bound[0] for bound in bounds_ingredientes)
    print(f"✅ Suma de límites mínimos: {suma_minimos}% (≤100%)")
    
    # Validar que cada límite mínimo sea menor o igual al máximo
    for i, (ing, bound) in enumerate(zip(ingredientes, bounds_ingredientes)):
        print(f"✅ {ing['nombre']}: {bound[0]}% ≤ {bound[1]}%")

    print("\n" + "="*60)
    print("PASO 3: AJUSTAR LÍMITES MÍNIMOS Y MÁXIMOS DE NUTRIENTES")
    print("="*60)
    
    # La matriz ya fue construida en el diagnóstico temprano, solo imprimir para debug
    for i, req in enumerate(requerimientos):
        print(f"🧪 {req['nombre']} ({tipo_optimizacion}): aportes por ingrediente = {matriz_nutrientes[i]}")

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
        
        # Realizar diagnóstico detallado del fallo
        diagnosticos_fallo = diagnosticar_fallo_optimizacion(ingredientes, requerimientos, bounds_ingredientes, matriz_nutrientes)
        
        # Agregar diagnósticos específicos de convergencia
        diagnosticos_fallo.append({
            'tipo': 'convergencia_fallida',
            'titulo': 'El algoritmo de optimización no pudo converger',
            'mensaje': 'Se probaron múltiples métodos de optimización pero ninguno encontró una solución factible.',
            'solucion': 'Revisa los límites de ingredientes y requerimientos nutricionales. Puede que las restricciones sean demasiado estrictas o incompatibles entre sí.',
            'detalles': [
                f'Métodos probados: {len(puntos_iniciales)} configuraciones diferentes',
                f'Ingredientes: {len(ingredientes)}',
                f'Requerimientos: {len(requerimientos)}',
                f'Restricciones totales: {len(todas_restricciones)}'
            ]
        })
        
        return jsonify({
            'error': 'No se pudo encontrar una solución factible',
            'diagnosticos': diagnosticos_fallo
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
        print(f"❌ Mensaje del optimizador: {resultado.message}")
        
        # Crear diagnóstico específico para fallo del optimizador
        diagnostico_optimizador = {
            'tipo': 'optimizador_fallo',
            'titulo': 'El optimizador reportó un error',
            'mensaje': f'Mensaje del sistema: {resultado.message}',
            'solucion': 'Revisa los datos de entrada y ajusta los límites para hacer el problema más factible.',
            'detalles': [
                f'Código de salida: {getattr(resultado, "status", "No disponible")}',
                f'Número de iteraciones: {getattr(resultado, "nit", "No disponible")}',
                f'Función objetivo final: {getattr(resultado, "fun", "No disponible")}'
            ]
        }
        
        return jsonify({
            'error': 'La optimización falló durante la ejecución',
            'diagnostico': diagnostico_optimizador
        }), 400

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
