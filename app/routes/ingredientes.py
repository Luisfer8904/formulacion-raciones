from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.db import get_db_connection, to_decimal
from app.routes.usuarios import registrar_actividad
from typing import Any

ingredientes_bp = Blueprint('ingredientes_bp', __name__)

@ingredientes_bp.route('/ingredientes')
def ver_ingredientes():
    if 'user_id' not in session:
        return redirect(url_for('auth_bp.login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, nombre, comentario, tipo, precio, ms FROM ingredientes WHERE usuario_id = %s", (session['user_id'],))
    ingredientes = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('operaciones/ingredientes.html', ingredientes=ingredientes)

@ingredientes_bp.route('/ver_ingrediente/<int:id>')
def ver_ingrediente(id):
    if 'user_id' not in session:
        flash('Debes iniciar sesión.', 'error')
        return redirect(url_for('auth_bp.login'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM ingredientes WHERE id = %s", (id,))
        ingrediente = cursor.fetchone()

        cursor.execute("""
            SELECT n.id, n.nombre, n.unidad, inut.valor
            FROM ingredientes_nutrientes AS inut
            JOIN nutrientes AS n ON inut.nutriente_id = n.id
            WHERE inut.ingrediente_id = %s AND (n.usuario_id = %s OR n.usuario_id IS NULL) AND inut.valor IS NOT NULL
        """, (id, session['user_id']))
        nutrientes = cursor.fetchall()

        cursor.close()
        conn.close()

        if not ingrediente:
            flash('Ingrediente no encontrado.', 'warning')
            return redirect(url_for('ingredientes_bp.ver_ingredientes'))

        return render_template('operaciones/ver_ingrediente.html', ingrediente=ingrediente, nutrientes=nutrientes)

    except Exception as e:
        print("❌ Error al cargar detalles del ingrediente:", e)
        flash('Error al cargar los detalles del ingrediente.', 'danger')
        return redirect(url_for('ingredientes_bp.ver_ingredientes'))

@ingredientes_bp.route('/api/ingrediente/<int:id>')
def api_ingrediente(id):
    try:
        # Validar que el usuario esté autenticado y que user_id esté en session
        if 'user_id' not in session:
            return jsonify({'error': 'No autorizado'}), 401

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM ingredientes WHERE id = %s", (id,))
        ingrediente: Any = cursor.fetchone()

        cursor.execute("""
            SELECT n.id, n.nombre, n.unidad, inut.valor
            FROM ingredientes_nutrientes AS inut
            JOIN nutrientes AS n ON inut.nutriente_id = n.id
            WHERE inut.ingrediente_id = %s AND (n.usuario_id = %s OR n.usuario_id IS NULL) AND inut.valor IS NOT NULL
        """, (id, session['user_id']))
        nutrientes = cursor.fetchall()

        cursor.close()
        conn.close()

        if not ingrediente:
            return jsonify({'error': 'Ingrediente no encontrado'}), 404

        # Crear respuesta JSON manualmente
        response_data = {
            'id': ingrediente['id'] if ingrediente else None,
            'nombre': ingrediente['nombre'] if ingrediente else None,
            'tipo': ingrediente['tipo'] if ingrediente else None,
            'comentario': ingrediente['comentario'] if ingrediente else None,
            'precio': ingrediente['precio'] if ingrediente else None,
            'ms': ingrediente['ms'] if ingrediente else None,
            'nutrientes': nutrientes if nutrientes else []
        }
        return jsonify(response_data)

    except Exception as e:
        print("❌ Error al obtener datos del ingrediente (API):", e)
        return jsonify({'error': 'Error interno del servidor'}), 500

@ingredientes_bp.route('/nuevo_ingrediente')
def nuevo_ingrediente():
    if 'user_id' not in session:
        return redirect(url_for('auth_bp.login'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT MAX(id) FROM ingredientes")
        result: Any = cursor.fetchone()
        ultimo_id = result['MAX(id)'] if result and result['MAX(id)'] else 0
        nuevo_id = ultimo_id + 1

        cursor.execute("SELECT id, nombre FROM especies")
        especies = cursor.fetchall()

        cursor.close()
        conn.close()
    except Exception as e:
        print("❌ Error al obtener datos:", e)
        nuevo_id = 1
        especies = []

    return render_template('operaciones/nuevo_ingrediente.html', ultimo_id=nuevo_id, especies=especies, mostrar_ms=True)

@ingredientes_bp.route('/guardar_ingrediente', methods=['POST'])
def guardar_ingrediente():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para guardar ingredientes.', 'error')
        return redirect(url_for('auth_bp.login'))

    # Validaciones backend
    nombre = request.form.get('nombre')
    comentario = request.form.get('comentario')
    tipo = request.form.get('tipo')
    precio = request.form.get('precio')
    ms = request.form.get('ms')

    if not nombre or nombre.strip() == '':
        flash('El nombre del ingrediente es obligatorio.', 'danger')
        return redirect(url_for('ingredientes_bp.nuevo_ingrediente'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Debug print de los datos recibidos antes de insertar
        print("➡️ Datos recibidos:", nombre, comentario, None, session.get('user_id'), tipo, precio, ms)
        print("🧪 Guardando MS:", ms)

        cursor.execute("""
            INSERT INTO ingredientes (nombre, comentario, tipo, usuario_id, precio, ms)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            nombre.strip(),
            comentario,
            tipo,
            session['user_id'],
            to_decimal(precio),
            to_decimal(ms)
        ))

        # Obtener el ID del nuevo ingrediente
        ingrediente_id = cursor.lastrowid
        print("🆕 ID del nuevo ingrediente:", ingrediente_id)

        # Guardar los nutrientes dinámicos
        for key, value in request.form.items():
            if key.startswith('nutriente_') and value.strip() != '':
                try:
                    nutriente_id = int(key.replace('nutriente_', ''))
                    valor = to_decimal(value)
                    if valor is not None:
                        cursor.execute("""
                            INSERT INTO ingredientes_nutrientes (ingrediente_id, nutriente_id, valor)
                            VALUES (%s, %s, %s)
                        """, (ingrediente_id, nutriente_id, valor))
                except Exception as e:
                    print(f"❌ Error guardando nutriente {key}: {e}")

        # Guardar las especies destino
        especies_destino = request.form.getlist('especies')
        for especie_id in especies_destino:
            try:
                cursor.execute("""
                    INSERT INTO ingrediente_especie (ingrediente_id, especie_id)
                    VALUES (%s, %s)
                """, (ingrediente_id, int(especie_id)))
            except Exception as e:
                print(f"❌ Error al guardar especie destino {especie_id}: {e}")

        conn.commit()
        cursor.close()
        conn.close()

        # Registrar actividad
        registrar_actividad(session['user_id'], f'Creó el ingrediente: {nombre.strip()}', 'ingrediente')

        flash('Ingrediente guardado correctamente.', 'success')
        return redirect(url_for('ingredientes_bp.ver_ingredientes'))

    except Exception as e:
        print("❌ Error al guardar ingrediente:", e)
        flash('Ocurrió un error al guardar el ingrediente.', 'danger')
        return redirect(url_for('ingredientes_bp.nuevo_ingrediente'))

@ingredientes_bp.route('/editar_ingrediente/<int:id>', methods=['GET', 'POST'])
def editar_ingrediente(id):
    if 'user_id' not in session:
        return redirect(url_for('auth_bp.login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        ms = request.form.get('ms')
        cursor.execute("""
            UPDATE ingredientes
            SET nombre=%s, tipo=%s, comentario=%s, precio=%s, ms=%s
            WHERE id=%s
        """, (
            nombre,
            request.form.get('tipo'),
            request.form.get('comentario'),
            to_decimal(request.form.get('precio')),
            to_decimal(request.form.get('ms')),
            id
        ))

        # Actualizar valores de nutrientes
        for key, value in request.form.items():
            if key.startswith('nutriente_'):
                try:
                    nutriente_id = int(key.replace('nutriente_', ''))
                    valor = to_decimal(value)
                    if valor is not None:
                        # Eliminar registros previos antes de insertar
                        cursor.execute("""
                            DELETE FROM ingredientes_nutrientes
                            WHERE ingrediente_id = %s AND nutriente_id = %s
                        """, (id, nutriente_id))

                        cursor.execute("""
                            INSERT INTO ingredientes_nutrientes (ingrediente_id, nutriente_id, valor)
                            VALUES (%s, %s, %s)
                        """, (id, nutriente_id, valor))
                except Exception as e:
                    print(f"❌ Error al actualizar nutriente {key}: {e}")

        conn.commit()
        cursor.close()
        conn.close()
        
        # Registrar actividad
        registrar_actividad(session['user_id'], f'Editó el ingrediente: {nombre}', 'ingrediente')
        
        flash('Ingrediente actualizado con éxito.', 'success')
        return redirect(url_for('ingredientes_bp.ver_ingredientes'))

    cursor.execute("SELECT * FROM ingredientes WHERE id = %s", (id,))
    ingrediente: Any = cursor.fetchone()
    # Asegurarse de que los campos 'comentario' y 'precio' estén presentes en el diccionario
    if ingrediente is not None:
        if 'comentario' not in ingrediente:
            ingrediente['comentario'] = ''
        if 'precio' not in ingrediente:
            ingrediente['precio'] = 0.0

    # Obtener nutrientes y valores actuales del ingrediente, filtrando por usuario_id
    cursor.execute("""
        SELECT n.id, n.nombre, n.unidad, inut.valor
        FROM nutrientes AS n
        LEFT JOIN ingredientes_nutrientes AS inut
            ON n.id = inut.nutriente_id AND inut.ingrediente_id = %s
        WHERE n.usuario_id = %s
    """, (id, session['user_id']))
    nutrientes = cursor.fetchall()

    cursor.close()
    conn.close()

    if ingrediente is None:
        flash('Ingrediente no encontrado.', 'warning')
        return redirect(url_for('ingredientes_bp.ver_ingredientes'))

    return render_template('operaciones/editar_ingrediente.html', ingrediente=ingrediente, nutrientes=nutrientes)

@ingredientes_bp.route('/actualizar_ingrediente/<int:id>', methods=['POST'])
def actualizar_ingrediente(id):
    if 'user_id' not in session:
        flash('Debes iniciar sesión.', 'error')
        return redirect(url_for('auth_bp.login'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE ingredientes SET
                nombre=%s, comentario=%s, tipo=%s
            WHERE id=%s
        """, (
            request.form.get('nombre'),
            request.form.get('comentario'),
            request.form.get('tipo'),
            id
        ))

        conn.commit()
        cursor.close()
        conn.close()

        flash('Ingrediente actualizado con éxito.', 'success')
        return redirect(url_for('ingredientes_bp.ver_ingredientes'))

    except Exception as e:
        print("❌ Error al actualizar:", e)
        flash('Ocurrió un error al actualizar.', 'danger')
        return redirect(url_for('ingredientes_bp.editar_ingrediente', id=id))

@ingredientes_bp.route('/eliminar_ingrediente/<int:id>')
def eliminar_ingrediente(id):
    if 'user_id' not in session:
        flash('Debes iniciar sesión.', 'error')
        return redirect(url_for('auth_bp.login'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Obtener el nombre del ingrediente antes de eliminarlo
        cursor.execute("SELECT nombre FROM ingredientes WHERE id = %s", (id,))
        ingrediente: Any = cursor.fetchone()
        nombre_ingrediente = ingrediente['nombre'] if ingrediente else f'ID {id}'
        
        # Eliminar relaciones en ingrediente_especie antes de eliminar el ingrediente
        cursor.execute("DELETE FROM ingrediente_especie WHERE ingrediente_id = %s", (id,))
        cursor.execute("DELETE FROM ingredientes WHERE id = %s", (id,))
        cursor.execute("DELETE FROM ingredientes_nutrientes WHERE ingrediente_id = %s", (id,))
        conn.commit()
        cursor.close()
        conn.close()

        # Registrar actividad
        registrar_actividad(session['user_id'], f'Eliminó el ingrediente: {nombre_ingrediente}', 'ingrediente')

        flash('Ingrediente eliminado correctamente.', 'success')
    except Exception as e:
        print("❌ Error al eliminar ingrediente:", e)
        flash('Error al eliminar el ingrediente.', 'danger')

    return redirect(url_for('ingredientes_bp.ver_ingredientes'))
