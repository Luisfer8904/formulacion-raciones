from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.db import get_db_connection
from app.routes.usuarios import registrar_actividad
from typing import Any, Union

mezclas_bp = Blueprint('mezclas_bp', __name__)

def safe_int(value: Any, default: int = 0) -> int:
    """Convierte un valor a entero de manera segura"""
    try:
        if value is None:
            return default
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_float(value: Any, default: float = 0.0) -> float:
    """Convierte un valor a float de manera segura"""
    try:
        if value is None:
            return default
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_str(value: Any, default: str = '') -> str:
    """Convierte un valor a string de manera segura"""
    try:
        if value is None:
            return default
        return str(value)
    except (ValueError, TypeError):
        return default

@mezclas_bp.route('/mezclas')
def ver_mezclas():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para acceder.', 'error')
        return redirect(url_for('auth_bp.login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id, nombre, tipo_animales, etapa_produccion, fecha_creacion FROM mezclas WHERE usuario_id = %s", (session['user_id'],))
    mezclas = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('operaciones/mezclas.html', mezclas=mezclas)

@mezclas_bp.route('/mezcla/<int:mezcla_id>')
def ver_mezcla_detalle(mezcla_id):
    if 'user_id' not in session:
        flash('Debes iniciar sesión.', 'error')
        return redirect(url_for('auth_bp.login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Obtener la mezcla
    cursor.execute("SELECT * FROM mezclas WHERE id = %s AND usuario_id = %s", (mezcla_id, session['user_id']))
    mezcla: Any = cursor.fetchone()

    if not mezcla:
        cursor.close()
        conn.close()
        flash('Mezcla no encontrada.', 'warning')
        return redirect(url_for('mezclas_bp.ver_mezclas'))

    # Obtener ingredientes de la mezcla
    cursor.execute("""
        SELECT mi.*, i.nombre AS nombre_ingrediente
        FROM mezcla_ingredientes mi
        JOIN ingredientes i ON mi.ingrediente_id = i.id
        WHERE mi.mezcla_id = %s
    """, (mezcla_id,))
    ingredientes = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('operaciones/mezcla_detalle.html', mezcla=mezcla, ingredientes=ingredientes)

@mezclas_bp.route('/cargar_mezcla/<int:mezcla_id>')
def cargar_mezcla(mezcla_id):
    if 'user_id' not in session:
        flash('Debes iniciar sesión para continuar.', 'error')
        return redirect(url_for('auth_bp.login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Obtener mezcla
    cursor.execute("SELECT * FROM mezclas WHERE id = %s AND usuario_id = %s", (mezcla_id, session['user_id']))
    mezcla: Any = cursor.fetchone()

    if not mezcla:
        cursor.close()
        conn.close()
        flash('Mezcla no encontrada.', 'warning')
        return redirect(url_for('mezclas_bp.lista_mezclas'))

    # Obtener ingredientes de la mezcla
    cursor.execute("""
        SELECT mi.*, i.nombre AS nombre_ingrediente, i.precio, i.ms
        FROM mezcla_ingredientes mi
        JOIN ingredientes i ON mi.ingrediente_id = i.id
        WHERE mi.mezcla_id = %s
    """, (mezcla_id,))
    ingredientes_mezcla = cursor.fetchall()
    print("🧪 Ingredientes mezcla:", ingredientes_mezcla)

    # Obtener todos los ingredientes del usuario para el select
    cursor.execute("SELECT id, nombre, comentario, ms, precio FROM ingredientes WHERE usuario_id = %s", (session['user_id'],))
    ingredientes_raw = cursor.fetchall()

    # Obtener nutrientes del usuario
    cursor.execute("SELECT id, nombre, unidad FROM nutrientes WHERE usuario_id = %s", (session['user_id'],))
    nutrientes_info = cursor.fetchall()

    ingredientes = []
    for ing in ingredientes_raw:
        ing_typed: Any = ing
        ingrediente = {
            'id': ing_typed['id'],
            'nombre': ing_typed['nombre'],
            'precio': float(ing_typed.get('precio', 0.0)) if hasattr(ing_typed, 'get') else 0.0,
            'comentario': ing_typed.get('comentario', '') if hasattr(ing_typed, 'get') else '',
            'ms': float(ing_typed.get('ms', 100)) if hasattr(ing_typed, 'get') else 100.0,
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
            valor = float(result['valor']) if result and result['valor'] is not None else 0.0
            ingrediente['nutrientes'].append({
                'id': nutriente_typed['id'],
                'nombre': nutriente_typed['nombre'],
                'valor': valor
            })
        ingredientes.append(ingrediente)

    print("📋 Ingredientes disponibles:", ingredientes)

    # Obtener configuración del usuario
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

    # Obtener todas las mezclas disponibles para el modal "Guardar Como"
    cursor.execute("SELECT nombre FROM mezclas WHERE usuario_id = %s ORDER BY nombre", (session['user_id'],))
    mezclas_disponibles = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('operaciones/formulacion_minerales.html',
                           mezcla=mezcla,
                           ingredientes_mezcla=ingredientes_mezcla,
                           minerales=ingredientes,
                           nutrientes=nutrientes_info,
                           ingredientesPrecargados=ingredientes_mezcla,
                           config_usuario=config_usuario,
                           mezclas_disponibles=mezclas_disponibles)

@mezclas_bp.route('/lista_mezclas')
def lista_mezclas():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para continuar.', 'error')
        return redirect(url_for('auth_bp.login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, nombre, tipo_animales, etapa_produccion, fecha_creacion
        FROM mezclas
        WHERE usuario_id = %s
        ORDER BY fecha_creacion DESC
    """, (session['user_id'],))

    mezclas = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('operaciones/lista_mezclas.html', mezclas=mezclas)

@mezclas_bp.route('/guardar_mezcla', methods=['POST'])
def guardar_mezcla():
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401

    data = request.get_json()
    nombre = data.get('nombre', '').strip()
    tipo_animales = data.get('tipo_animales', '').strip()
    etapa_produccion = data.get('etapa_produccion', '').strip()
    observaciones = data.get('observaciones', '').strip()
    ingredientes = data.get('ingredientes', [])
    # Recoger nutrientes enviados desde el frontend
    nutrientes = data.get('nutrientes', [])

    if not nombre:
        return jsonify({'error': 'El nombre de la mezcla es obligatorio.'}), 400

    if not ingredientes:
        return jsonify({'error': 'Debe incluir al menos un ingrediente.'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insertar en la tabla mezclas incluyendo los nuevos campos y fecha_creacion
        cursor.execute("""
            INSERT INTO mezclas (usuario_id, nombre, tipo_animales, etapa_produccion, observaciones, fecha_creacion)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, (safe_int(session['user_id']), safe_str(nombre), safe_str(tipo_animales), safe_str(etapa_produccion), safe_str(observaciones)))
        mezcla_id = cursor.lastrowid

        # Insertar ingredientes de la mezcla
        for ing in ingredientes:
            ingrediente_id = ing.get('ingrediente_id')
            inclusion = ing.get('inclusion')

            if ingrediente_id is not None and inclusion is not None:
                # Validar que los valores no sean None antes de convertir
                ingrediente_id_int = safe_int(ingrediente_id)
                inclusion_float = safe_float(inclusion)
                if ingrediente_id_int > 0 and inclusion_float >= 0:
                    cursor.execute("""
                        INSERT INTO mezcla_ingredientes (mezcla_id, ingrediente_id, inclusion)
                        VALUES (%s, %s, %s)
                    """, (safe_int(mezcla_id), ingrediente_id_int, inclusion_float))

        # Eliminar registros antiguos de nutrientes para la mezcla (si existieran)
        cursor.execute("DELETE FROM mezcla_ingredientes_nutrientes WHERE mezcla_id = %s", (safe_int(mezcla_id),))

        # Insertar los nutrientes seleccionados si hay alguno (recibidos como lista de objetos con nutriente_id)
        for n in nutrientes:
            nutriente_id = n.get('nutriente_id') or n.get('id')
            if nutriente_id is not None:
                # Asegurar que nutriente_id sea un entero válido
                nutriente_id_int = safe_int(nutriente_id)
                if nutriente_id_int > 0:
                    cursor.execute(
                        "INSERT INTO mezcla_ingredientes_nutrientes (mezcla_id, nutriente_id) VALUES (%s, %s)",
                        (safe_int(mezcla_id), nutriente_id_int)
                    )

        conn.commit()
        cursor.close()
        conn.close()

        # Registrar actividad
        registrar_actividad(session['user_id'], f'Guardó la formulación: {nombre}', 'formulacion')

        return jsonify({'mensaje': 'Mezcla guardada exitosamente.'}), 200

    except Exception as e:
        print("❌ Error al guardar mezcla:", e)
        return jsonify({'error': f'Error al guardar mezcla: {str(e)}'}), 500

@mezclas_bp.route('/guardar_mezcla_como', methods=['POST'])
def guardar_mezcla_como():
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401

    data = request.get_json()
    nombre = data.get('nombre', '').strip()
    tipo_animales = data.get('tipo_animales', '').strip()
    etapa_produccion = data.get('etapa_produccion', '').strip()
    observaciones = data.get('observaciones', '').strip()
    ingredientes = data.get('ingredientes', [])

    if not nombre:
        return jsonify({'error': 'El nombre es obligatorio.'}), 400

    if not ingredientes:
        return jsonify({'error': 'Debe incluir al menos un ingrediente.'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Crear una nueva mezcla en lugar de actualizar
        cursor.execute("""
            INSERT INTO mezclas (usuario_id, nombre, tipo_animales, etapa_produccion, observaciones, fecha_creacion)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, (safe_int(session['user_id']), safe_str(nombre), safe_str(tipo_animales), safe_str(etapa_produccion), safe_str(observaciones)))
        nueva_mezcla_id = cursor.lastrowid

        for ing in ingredientes:
            ingrediente_id = ing.get('ingrediente_id')
            inclusion = ing.get('inclusion')

            if ingrediente_id is not None and inclusion is not None:
                cursor.execute("""
                    INSERT INTO mezcla_ingredientes (mezcla_id, ingrediente_id, inclusion)
                    VALUES (%s, %s, %s)
                """, (safe_int(nueva_mezcla_id), safe_int(ingrediente_id), safe_float(inclusion)))

        # Guardar nutrientes asociados
        nutrientes = data.get('nutrientes', [])
        for nutriente in nutrientes:
            nutriente_id = nutriente.get('id')
            if nutriente_id:
                # Asegurar que nutriente_id sea un entero válido
                nutriente_id_int = safe_int(nutriente_id)
                if nutriente_id_int > 0:
                    cursor.execute("""
                        INSERT INTO mezcla_ingredientes_nutrientes (mezcla_id, nutriente_id)
                        VALUES (%s, %s)
                    """, (safe_int(nueva_mezcla_id), nutriente_id_int))

        conn.commit()
        cursor.close()
        conn.close()

        # Registrar actividad
        registrar_actividad(session['user_id'], f'Guardó como nueva formulación: {nombre}', 'formulacion')

        return jsonify({'mensaje': 'Mezcla guardada exitosamente.'}), 200

    except Exception as e:
        print("❌ Error al guardar mezcla (Guardar Como):", e)
        return jsonify({'error': f'Error al guardar mezcla: {str(e)}'}), 500

@mezclas_bp.route('/eliminar_mezcla/<int:mezcla_id>')
def eliminar_mezcla(mezcla_id):
    if 'user_id' not in session:
        flash('Debes iniciar sesión.', 'error')
        return redirect(url_for('auth_bp.login'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Obtener el nombre de la mezcla antes de eliminarla
        cursor.execute("SELECT nombre FROM mezclas WHERE id = %s AND usuario_id = %s", (mezcla_id, session['user_id']))
        mezcla: Any = cursor.fetchone()
        nombre_mezcla = mezcla['nombre'] if mezcla else f'ID {mezcla_id}'

        # Eliminar ingredientes asociados a la mezcla
        cursor.execute("DELETE FROM mezcla_ingredientes WHERE mezcla_id = %s", (mezcla_id,))
        # Eliminar la mezcla principal
        cursor.execute("DELETE FROM mezclas WHERE id = %s AND usuario_id = %s", (mezcla_id, session['user_id']))

        conn.commit()
        cursor.close()
        conn.close()

        # Registrar actividad
        registrar_actividad(session['user_id'], f'Eliminó la formulación: {nombre_mezcla}', 'formulacion')

        flash('Mezcla eliminada correctamente.', 'success')
    except Exception as e:
        print(f"❌ Error al eliminar mezcla: {e}")
        flash('Error al eliminar la mezcla.', 'danger')

    return redirect(url_for('mezclas_bp.ver_mezclas'))

@mezclas_bp.route('/actualizar_mezcla', methods=['POST'])
def actualizar_mezcla():
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401

    data = request.get_json()
    nombre = data.get('nombre', '').strip()
    tipo_animales = data.get('tipo_animales', '').strip()
    etapa_produccion = data.get('etapa_produccion', '').strip()
    observaciones = data.get('observaciones', '').strip()
    ingredientes = data.get('ingredientes', [])
    nutrientes = data.get('nutrientes', [])

    if not nombre:
        return jsonify({'error': 'El nombre de la mezcla es obligatorio.'}), 400

    if not ingredientes:
        return jsonify({'error': 'Debe incluir al menos un ingrediente.'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Buscar la mezcla existente por nombre y usuario
        cursor.execute("SELECT id FROM mezclas WHERE nombre = %s AND usuario_id = %s", (safe_str(nombre), safe_int(session['user_id'])))
        mezcla_existente = cursor.fetchone()

        if mezcla_existente:
            mezcla_id = mezcla_existente['id'] if isinstance(mezcla_existente, dict) else mezcla_existente[0]
            
            # Actualizar la mezcla existente
            cursor.execute("""
                UPDATE mezclas 
                SET tipo_animales = %s, etapa_produccion = %s, observaciones = %s, fecha_creacion = NOW()
                WHERE id = %s AND usuario_id = %s
            """, (safe_str(tipo_animales), safe_str(etapa_produccion), safe_str(observaciones), safe_int(mezcla_id), safe_int(session['user_id'])))

            # Eliminar ingredientes antiguos
            cursor.execute("DELETE FROM mezcla_ingredientes WHERE mezcla_id = %s", (safe_int(mezcla_id),))
            
            # Eliminar nutrientes antiguos
            cursor.execute("DELETE FROM mezcla_ingredientes_nutrientes WHERE mezcla_id = %s", (safe_int(mezcla_id),))
        else:
            # Crear nueva mezcla si no existe
            cursor.execute("""
                INSERT INTO mezclas (usuario_id, nombre, tipo_animales, etapa_produccion, observaciones, fecha_creacion)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """, (safe_int(session['user_id']), safe_str(nombre), safe_str(tipo_animales), safe_str(etapa_produccion), safe_str(observaciones)))
            mezcla_id = cursor.lastrowid

        # Insertar nuevos ingredientes
        for ing in ingredientes:
            ingrediente_id = ing.get('ingrediente_id')
            inclusion = ing.get('inclusion')

            if ingrediente_id is not None and inclusion is not None:
                # Validar que los valores no sean None antes de convertir
                ingrediente_id_int = safe_int(ingrediente_id)
                inclusion_float = safe_float(inclusion)
                if ingrediente_id_int > 0 and inclusion_float >= 0:
                    cursor.execute("""
                        INSERT INTO mezcla_ingredientes (mezcla_id, ingrediente_id, inclusion)
                        VALUES (%s, %s, %s)
                    """, (safe_int(mezcla_id), ingrediente_id_int, inclusion_float))

        # Insertar nuevos nutrientes
        for nutriente_id in nutrientes:
            if nutriente_id:
                # Validar que nutriente_id no sea None antes de convertir
                nutriente_id_int = safe_int(nutriente_id)
                if nutriente_id_int > 0:
                    cursor.execute("""
                        INSERT INTO mezcla_ingredientes_nutrientes (mezcla_id, nutriente_id)
                        VALUES (%s, %s)
                    """, (safe_int(mezcla_id), nutriente_id_int))

        conn.commit()
        cursor.close()
        conn.close()

        mensaje = 'Mezcla actualizada exitosamente.' if mezcla_existente else 'Mezcla creada exitosamente.'
        return jsonify({'success': True, 'mensaje': mensaje}), 200

    except Exception as e:
        print("❌ Error al actualizar mezcla:", e)
        return jsonify({'error': f'Error al actualizar mezcla: {str(e)}'}), 500

@mezclas_bp.route('/api/lista_mezclas', methods=['GET'])
def api_lista_mezclas():
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id, nombre FROM mezclas WHERE usuario_id = %s ORDER BY nombre ASC", (session['user_id'],))
    mezclas = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(mezclas)
