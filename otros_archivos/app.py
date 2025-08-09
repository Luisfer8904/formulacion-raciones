from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import mysql.connector
import re
import numpy as np

app = Flask(__name__)
app.secret_key = 'clave_segura'

@app.route('/opciones')
def opciones():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para acceder a las opciones.', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT nombre, email, pais, moneda, tipo_moneda, unidad_medida, idioma, tema
        FROM usuarios
        WHERE id = %s
    """, (session['user_id'],))

    usuario = cursor.fetchone() or {}

    cursor.close()
    conn.close()

    return render_template('operaciones/opciones.html', usuario=usuario)


@app.route('/guardar_opciones', methods=['POST'])
def guardar_opciones():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para guardar opciones.', 'error')
        return redirect(url_for('login'))

    nombre = request.form.get('nombre')
    email = request.form.get('email')
    pais = request.form.get('pais')
    moneda = request.form.get('moneda')
    tipo_moneda = request.form.get('tipo_moneda')
    unidad_medida = request.form.get('unidad_medida')
    idioma = request.form.get('idioma')
    tema = request.form.get('tema')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE usuarios SET 
                nombre = %s,
                email = %s,
                pais = %s,
                moneda = %s,
                tipo_moneda = %s,
                unidad_medida = %s,
                idioma = %s,
                tema = %s
            WHERE id = %s
        """, (nombre, email, pais, moneda, tipo_moneda, unidad_medida, idioma, tema, session['user_id']))

        conn.commit()
        cursor.close()
        conn.close()

        flash('Configuración guardada correctamente.', 'success')
        return redirect(url_for('opciones'))
    except Exception as e:
        print("❌ Error al guardar opciones:", e)
        flash('Error al guardar la configuración.', 'danger')
        return redirect(url_for('opciones'))
# Filtro personalizado para reemplazo con regex en plantillas Jinja2
@app.template_filter('regex_replace')
def regex_replace(s, find, replace):
    return re.sub(find, replace, s)
# === Ruta para ver detalles de un ingrediente ===
@app.route('/ver_ingrediente/<int:id>')
def ver_ingrediente(id):
    if 'user_id' not in session:
        flash('Debes iniciar sesión.', 'error')
        return redirect(url_for('login'))

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
            return redirect(url_for('ver_ingredientes'))

        return render_template('operaciones/ver_ingrediente.html', ingrediente=ingrediente, nutrientes=nutrientes)

    except Exception as e:
        print("❌ Error al cargar detalles del ingrediente:", e)
        flash('Error al cargar los detalles del ingrediente.', 'danger')
        return redirect(url_for('ver_ingredientes'))
@app.route('/api/ingrediente/<int:id>')
def api_ingrediente(id):
    try:
        # Validar que el usuario esté autenticado y que user_id esté en session
        if 'user_id' not in session:
            return jsonify({'error': 'No autorizado'}), 401

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
            return jsonify({'error': 'Ingrediente no encontrado'}), 404

        ingrediente['nutrientes'] = nutrientes if nutrientes else []
        return jsonify(ingrediente)

    except Exception as e:
        print("❌ Error al obtener datos del ingrediente (API):", e)
        return jsonify({'error': 'Error interno del servidor'}), 500
# Función para obtener los nutrientes disponibles desde la base de datos
def obtener_nutrientes_disponibles():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM nutrientes")
    resultados = cursor.fetchall()
    cursor.close()
    conn.close()

    nutrientes = [r[0] for r in resultados]
    return nutrientes
# (imports, app, and secret_key moved to top)
# Configuración de conexión
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": "3306",
    "database": "formulacion_nutricional",
    "user": "root",
    "password": "root1234"
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# Función para convertir valores a decimales válidos
def to_decimal(value):
    try:
        if not value or str(value).strip() == '':
            return None
        val = float(value.strip())
        return round(val, 4)
    except (ValueError, TypeError):
        return None

# Ruta raíz
@app.route('/')
def home():
    return render_template('sitio/index.html')

# Login de administrador
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form.get('correo')
        contrasena = request.form.get('contrasena')

        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios WHERE email = %s", (correo,))
            user = cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

        if user is None:
            flash('Usuario no encontrado.', 'error')
        elif 'password' not in user or user['password'] != contrasena:
            flash('Contraseña incorrecta o no definida.', 'error')
        elif user['rol'] not in ['admin', 'user']:
            flash('No tienes permisos para acceder a esta sección.', 'error')
        else:
            session['user_id'] = user['id']
            session['rol'] = user['rol']
            session['nombre'] = user['nombre']
            session['email'] = user['email']
            flash('Inicio de sesión exitoso.', 'success')
            return redirect(url_for('panel'))

    return render_template('sitio/login.html')

@app.route('/panel')
def panel():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para acceder al panel.', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Total de formulaciones (mezclas) del usuario
    cursor.execute("SELECT COUNT(*) FROM mezclas WHERE usuario_id = %s", (session['user_id'],))
    total_formulaciones = cursor.fetchone()[0]

    # Total de ingredientes del usuario
    cursor.execute("SELECT COUNT(*) FROM ingredientes WHERE usuario_id = %s", (session['user_id'],))
    total_ingredientes = cursor.fetchone()[0]

    # Total de reportes — por ahora puedes dejarlo en cero si no tienes reportes implementados
    total_reportes = 0

    # Historial de actividades vacío por el momento
    actividades = []

    cursor.close()
    conn.close()

    return render_template('operaciones/panel.html',
                           total_formulaciones=total_formulaciones,
                           total_ingredientes=total_ingredientes,
                           total_reportes=total_reportes,
                           actividades=actividades)

# Página del panel del formulador
@app.route('/panelformulador')
def panelformulador():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para acceder.', 'error')
        return redirect(url_for('login'))
    return redirect(url_for('formulacion_minerales'))


# Ver ingredientes
@app.route('/ingredientes')
def ver_ingredientes():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, nombre, comentario, tipo, precio, ms FROM ingredientes WHERE usuario_id = %s", (session['user_id'],))
    ingredientes = cursor.fetchall()
    cursor.close()
    conn.close()
    # NOTA: Para mostrar un botón "Eliminar" junto a cada ingrediente en la plantilla,
    # agrega este enlace dentro del bucle de ingredientes en 'operaciones/ingredientes.html':
    # (Remplazando el comentario por la línea real de HTML)
    #
    # <a href=\"{{ url_for('eliminar_ingrediente', id=ingrediente.id) }}\" class=\"btn btn-danger btn-sm\" onclick=\"return confirm('¿Estás seguro de que deseas eliminar este ingrediente?');\">Eliminar</a>
    #
    return render_template('operaciones/ingredientes.html', ingredientes=ingredientes)

@app.route('/editar_ingrediente/<int:id>', methods=['GET', 'POST'])
def editar_ingrediente(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

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
        flash('Ingrediente actualizado con éxito.', 'success')
        return redirect(url_for('ver_ingredientes'))

    cursor.execute("SELECT * FROM ingredientes WHERE id = %s", (id,))
    ingrediente = cursor.fetchone()
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
        return redirect(url_for('ver_ingredientes'))

    return render_template('operaciones/editar_ingrediente.html', ingrediente=ingrediente, nutrientes=nutrientes)

# Actualizar ingrediente
@app.route('/actualizar_ingrediente/<int:id>', methods=['POST'])
def actualizar_ingrediente(id):
    if 'user_id' not in session:
        flash('Debes iniciar sesión.', 'error')
        return redirect(url_for('login'))

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
        return redirect(url_for('ver_ingredientes'))

    except Exception as e:
        print("❌ Error al actualizar:", e)
        flash('Ocurrió un error al actualizar.', 'danger')
        return redirect(url_for('editar_ingrediente', id=id))

# Eliminar ingrediente
@app.route('/eliminar_ingrediente/<int:id>')
def eliminar_ingrediente(id):
    if 'user_id' not in session:
        flash('Debes iniciar sesión.', 'error')
        return redirect(url_for('login'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Eliminar relaciones en ingrediente_especie antes de eliminar el ingrediente
        cursor.execute("DELETE FROM ingrediente_especie WHERE ingrediente_id = %s", (id,))
        cursor.execute("DELETE FROM ingredientes WHERE id = %s", (id,))
        cursor.execute("DELETE FROM ingredientes_nutrientes WHERE ingrediente_id = %s", (id,))
        conn.commit()
        cursor.close()
        conn.close()

        flash('Ingrediente eliminado correctamente.', 'success')
    except Exception as e:
        print("❌ Error al eliminar ingrediente:", e)
        flash('Error al eliminar el ingrediente.', 'danger')

    return redirect(url_for('ver_ingredientes'))

@app.route('/nuevo_ingrediente')
def nuevo_ingrediente():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT MAX(id) FROM ingredientes")
        ultimo_id = cursor.fetchone()['MAX(id)'] or 0
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

@app.route('/guardar_ingrediente', methods=['POST'])
def guardar_ingrediente():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para guardar ingredientes.', 'error')
        return redirect(url_for('login'))

    # Validaciones backend
    nombre = request.form.get('nombre')
    comentario = request.form.get('comentario')
    tipo = request.form.get('tipo')
    precio = request.form.get('precio')
    ms = request.form.get('ms')

    if not nombre or nombre.strip() == '':
        flash('El nombre del ingrediente es obligatorio.', 'danger')
        return redirect(url_for('nuevo_ingrediente'))

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

        flash('Ingrediente guardado correctamente.', 'success')
        return redirect(url_for('ver_ingredientes'))

    except Exception as e:
        print("❌ Error al guardar ingrediente:", e)
        flash('Ocurrió un error al guardar el ingrediente.', 'danger')
        return redirect(url_for('nuevo_ingrediente'))

# Cerrar sesión
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Has cerrado sesión.', 'success')
    return redirect(url_for('home'))

@app.route('/mezclas')
def ver_mezclas():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para acceder.', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id, nombre, tipo_animales, etapa_produccion, fecha_creacion FROM mezclas WHERE usuario_id = %s", (session['user_id'],))
    mezclas = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('operaciones/mezclas.html', mezclas=mezclas)

# === Ruta para ver detalle de una mezcla ===
@app.route('/mezcla/<int:mezcla_id>')
def ver_mezcla_detalle(mezcla_id):
    if 'user_id' not in session:
        flash('Debes iniciar sesión.', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Obtener la mezcla
    cursor.execute("SELECT * FROM mezclas WHERE id = %s AND usuario_id = %s", (mezcla_id, session['user_id']))
    mezcla = cursor.fetchone()

    if not mezcla:
        cursor.close()
        conn.close()
        flash('Mezcla no encontrada.', 'warning')
        return redirect(url_for('ver_mezclas'))

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

@app.route('/cargar_mezcla/<int:mezcla_id>')
def cargar_mezcla(mezcla_id):
    if 'user_id' not in session:
        flash('Debes iniciar sesión para continuar.', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Obtener mezcla
    cursor.execute("SELECT * FROM mezclas WHERE id = %s AND usuario_id = %s", (mezcla_id, session['user_id']))
    mezcla = cursor.fetchone()

    if not mezcla:
        cursor.close()
        conn.close()
        flash('Mezcla no encontrada.', 'warning')
        return redirect(url_for('lista_mezclas'))

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
        ingrediente = {
            'id': ing['id'],
            'nombre': ing['nombre'],
            'precio': ing.get('precio', 0.0),
            'comentario': ing.get('comentario', ''),
            'ms': ing.get('ms', 100),
            'nutrientes': []
        }
        for nutriente in nutrientes_info:
            cursor.execute("""
                SELECT inut.valor 
                FROM ingredientes_nutrientes AS inut
                WHERE inut.ingrediente_id = %s AND inut.nutriente_id = %s
            """, (ing['id'], nutriente['id']))
            result = cursor.fetchone()
            valor = result['valor'] if result else 0.0
            ingrediente['nutrientes'].append({
                'id': nutriente['id'],
                'nombre': nutriente['nombre'],
                'valor': valor
            })
            ingrediente[nutriente['nombre']] = valor
        ingredientes.append(ingrediente)

    print("📋 Ingredientes disponibles:", ingredientes)

    cursor.close()
    conn.close()

    return render_template('operaciones/formulacion_minerales.html',
                           mezcla=mezcla,
                           ingredientes_mezcla=ingredientes_mezcla,
                           minerales=ingredientes,
                           nutrientes=nutrientes_info,
                           ingredientesPrecargados=ingredientes_mezcla)

@app.route('/formulacion_minerales')
def formulacion_minerales():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para acceder.', 'error')
        return redirect(url_for('login'))

    # Obtener mezcla_id si viene como parámetro de consulta (query string)
    mezcla_id = request.args.get('mezcla_id', default=None, type=int)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Obtener todos los ingredientes
    cursor.execute("SELECT id, nombre, comentario, ms, precio FROM ingredientes WHERE usuario_id = %s", (session['user_id'],))
    ingredientes_raw = cursor.fetchall()

    # Obtener todos los nutrientes disponibles filtrados por usuario (incluyendo id y unidad)
    cursor.execute("SELECT id, nombre, unidad FROM nutrientes WHERE usuario_id = %s", (session['user_id'],))
    nutrientes_info = cursor.fetchall()

    ingredientes = []
    for ing in ingredientes_raw:
        ingrediente = {
            'id': ing['id'],
            'nombre': ing['nombre'],
            'precio': ing.get('precio', 0.0),
            'comentario': ing.get('comentario', ''),
            'ms': ing.get('ms', 100),
            'nutrientes': []
        }
        for nutriente in nutrientes_info:
            cursor.execute("""
                SELECT inut.valor 
                FROM ingredientes_nutrientes AS inut
                WHERE inut.ingrediente_id = %s AND inut.nutriente_id = %s
            """, (ing['id'], nutriente['id']))
            result = cursor.fetchone()
            valor = result['valor'] if result else 0.0
            ingrediente['nutrientes'].append({
                'id': nutriente['id'],
                'nombre': nutriente['nombre'],
                'valor': valor
            })
            ingrediente[nutriente['nombre']] = valor
        ingredientes.append(ingrediente)

    # Obtener mezclas disponibles para el usuario (para mostrar en el formulario)
    cursor.execute("SELECT id, nombre FROM mezclas WHERE usuario_id = %s ORDER BY nombre ASC", (session['user_id'],))
    mezclas_disponibles = cursor.fetchall()

    # === BLOQUE NUEVO: obtener mezcla seleccionada y sus ingredientes si mezcla_id existe ===
    mezcla = None
    ingredientes_mezcla = []
    if mezcla_id:
        cursor.execute("SELECT * FROM mezclas WHERE id = %s AND usuario_id = %s", (mezcla_id, session['user_id']))
        mezcla = cursor.fetchone()

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
                           ingredientes_mezcla=ingredientes_mezcla)

# === Ruta para listar mezclas del usuario ===
@app.route('/lista_mezclas')
def lista_mezclas():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para continuar.', 'error')
        return redirect(url_for('login'))

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



@app.route('/guardar_mezcla', methods=['POST'])
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
        """, (session['user_id'], nombre, tipo_animales, etapa_produccion, observaciones))
        mezcla_id = cursor.lastrowid

        # Insertar ingredientes de la mezcla
        for ing in ingredientes:
            ingrediente_id = ing.get('ingrediente_id')
            inclusion = ing.get('inclusion')

            if ingrediente_id is not None and inclusion is not None:
                cursor.execute("""
                    INSERT INTO mezcla_ingredientes (mezcla_id, ingrediente_id, inclusion)
                    VALUES (%s, %s, %s)
                """, (mezcla_id, ingrediente_id, inclusion))

        # Eliminar registros antiguos de nutrientes para la mezcla (si existieran)
        cursor.execute("DELETE FROM mezcla_ingredientes_nutrientes WHERE mezcla_id = %s", (mezcla_id,))

        # Insertar los nutrientes seleccionados si hay alguno (recibidos como lista de objetos con nutriente_id)
        for n in nutrientes:
            nutriente_id = n.get('nutriente_id') or n.get('id')
            if nutriente_id is not None:
                cursor.execute(
                    "INSERT INTO mezcla_ingredientes_nutrientes (mezcla_id, nutriente_id) VALUES (%s, %s)",
                    (mezcla_id, nutriente_id)
                )

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'mensaje': 'Mezcla guardada exitosamente.'}), 200

    except Exception as e:
        print("❌ Error al guardar mezcla:", e)
        return jsonify({'error': f'Error al guardar mezcla: {str(e)}'}), 500



# === Nueva ruta: guardar_mezcla_como ===
@app.route('/guardar_mezcla_como', methods=['POST'])
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
        """, (session['user_id'], nombre, tipo_animales, etapa_produccion, observaciones))
        nueva_mezcla_id = cursor.lastrowid

        for ing in ingredientes:
            ingrediente_id = ing.get('ingrediente_id')
            inclusion = ing.get('inclusion')

            if ingrediente_id is not None and inclusion is not None:
                cursor.execute("""
                    INSERT INTO mezcla_ingredientes (mezcla_id, ingrediente_id, inclusion)
                    VALUES (%s, %s, %s)
                """, (nueva_mezcla_id, ingrediente_id, inclusion))

        # Guardar nutrientes asociados
        nutrientes = data.get('nutrientes', [])
        for nutriente in nutrientes:
            nutriente_id = nutriente.get('id')
            if nutriente_id:
                cursor.execute("""
                    INSERT INTO mezcla_ingredientes_nutrientes (mezcla_id, nutriente_id)
                    VALUES (%s, %s)
                """, (nueva_mezcla_id, nutriente_id))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'mensaje': 'Mezcla guardada exitosamente.'}), 200

    except Exception as e:
        print("❌ Error al guardar mezcla (Guardar Como):", e)
        return jsonify({'error': f'Error al guardar mezcla: {str(e)}'}), 500


from scipy.optimize import minimize
import numpy as np

@app.route('/optimizar_formulacion', methods=['POST'])
def optimizar_formulacion():
    from flask import request
    import json

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
            print(f"❌ Error: El ingrediente {ing['nombre']} no tiene estructura de nutrientes válida.")
            return jsonify({'error': f"El ingrediente {ing['nombre']} no tiene nutrientes cargados."}), 400

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
                return lambda x: np.dot(matriz_nutrientes[indice], x) - valor_min

            restricciones_nutrientes.append({
                'type': 'ineq',
                'fun': crear_restriccion_min(i, req_min)
            })
            print(f"✅ Restricción mínima para {nombre_nutriente} (base seca): ≥ {req_min}")

        if req_max is not None:
            def crear_restriccion_max(indice, valor_max):
                return lambda x: valor_max - np.dot(matriz_nutrientes[indice], x)

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
                valor += aporte_base_seca / 100  # Normalizar por 100% de mezcla
            else:
                if isinstance(nutrientes.get(nombre_nutriente), dict):
                    aporte_nutriente = float(nutrientes.get(nombre_nutriente, {}).get('valor_bs', 0))
                else:
                    aporte_nutriente = float(nutrientes.get(nombre_nutriente + '_bs', nutrientes.get(nombre_nutriente, 0)))
                valor += aporte_nutriente * inclusion / 100  # Asumiendo valores por 100%
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
            'inclusion': round(inclusion, 2),
            'peso': round(inclusion, 2),  # Para mezcla de 100 kg
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


# Ruta para mostrar la página de nutrientes en el frontend
@app.route('/nutrientes')
def ver_nutrientes():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para acceder.', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, nombre, unidad, tipo FROM nutrientes WHERE usuario_id = %s", (session['user_id'],))
    nutrientes = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('operaciones/ver_nutrientes.html', nutrientes=nutrientes)


# Ruta para mostrar el formulario de creación de un nuevo nutriente
@app.route('/nuevo_nutriente')
def nuevo_nutriente():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para acceder.', 'error')
        return redirect(url_for('login'))
    # El formulario debe tener: <form method="POST" action="{{ url_for('guardar_nutriente') }}">
    return render_template('operaciones/nuevo_nutriente.html')


# Guardar nuevo nutriente
@app.route('/guardar_nutriente', methods=['POST'])
def guardar_nutriente():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para guardar nutrientes.', 'error')
        return redirect(url_for('login'))

    nombre = request.form.get('nombre')
    unidad = request.form.get('unidad')
    tipo = request.form.get('tipo')

    if not nombre or not unidad or not tipo:
        flash('Todos los campos son obligatorios.', 'danger')
        return redirect(url_for('nuevo_nutriente'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO nutrientes (nombre, unidad, tipo, usuario_id) VALUES (%s, %s, %s, %s)", (nombre, unidad, tipo, session['user_id']))
        conn.commit()
        cursor.close()
        conn.close()

        flash('Nutriente guardado correctamente.', 'success')
        return redirect(url_for('ver_nutrientes'))
    except Exception as e:
        print("❌ Error al guardar nutriente:", e)
        flash('Ocurrió un error al guardar el nutriente.', 'danger')
        return redirect(url_for('nuevo_nutriente'))


# === Rutas para editar y eliminar nutrientes ===
@app.route('/editar_nutriente/<int:id>', methods=['GET', 'POST'])
def editar_nutriente(id):
    if 'user_id' not in session:
        flash('Debes iniciar sesión para continuar.', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        unidad = request.form.get('unidad')
        tipo = request.form.get('tipo')
        cursor.execute("UPDATE nutrientes SET nombre=%s, unidad=%s, tipo=%s WHERE id=%s AND usuario_id=%s", (nombre, unidad, tipo, id, session['user_id']))
        if cursor.rowcount == 0:
            flash('No tienes permisos para editar este nutriente.', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('ver_nutrientes'))
        conn.commit()
        flash('Nutriente actualizado correctamente.', 'success')
        cursor.close()
        conn.close()
        return redirect(url_for('ver_nutrientes'))

    cursor.execute("SELECT * FROM nutrientes WHERE id = %s AND usuario_id = %s", (id, session['user_id']))
    nutriente = cursor.fetchone()
    if not nutriente:
        flash('Nutriente no encontrado o sin permisos.', 'error')
        cursor.close()
        conn.close()
        return redirect(url_for('ver_nutrientes'))
    cursor.close()
    conn.close()

    # Renderiza la plantilla de edición de nutriente, asegurando que no se incluyan campos de precio ni comentario
    return render_template('operaciones/editar_nutriente.html', nutriente=nutriente)


@app.route('/eliminar_nutriente/<int:id>')
def eliminar_nutriente(id):
    if 'user_id' not in session:
        flash('Debes iniciar sesión para continuar.', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM nutrientes WHERE id = %s AND usuario_id = %s", (id, session['user_id']))
    if cursor.rowcount == 0:
        flash('No tienes permisos para eliminar este nutriente.', 'error')
        cursor.close()
        conn.close()
        return redirect(url_for('ver_nutrientes'))
    conn.commit()
    cursor.close()
    conn.close()

    flash('Nutriente eliminado correctamente.', 'success')
    return redirect(url_for('ver_nutrientes'))

@app.route('/eliminar_mezcla/<int:mezcla_id>')
def eliminar_mezcla(mezcla_id):
    if 'user_id' not in session:
        flash('Debes iniciar sesión.', 'error')
        return redirect(url_for('login'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Eliminar ingredientes asociados a la mezcla
        cursor.execute("DELETE FROM mezcla_ingredientes WHERE mezcla_id = %s", (mezcla_id,))
        # Eliminar la mezcla principal
        cursor.execute("DELETE FROM mezclas WHERE id = %s AND usuario_id = %s", (mezcla_id, session['user_id']))

        conn.commit()
        cursor.close()
        conn.close()

        flash('Mezcla eliminada correctamente.', 'success')
    except Exception as e:
        print(f"❌ Error al eliminar mezcla: {e}")
        flash('Error al eliminar la mezcla.', 'danger')

    return redirect(url_for('ver_mezclas'))

@app.route('/api/lista_mezclas', methods=['GET'])
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

@app.route('/requerimientos')
def requerimientos():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para acceder.', 'error')
        return redirect(url_for('login'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Obtener datos de la tabla requerimientos filtrados por usuario_id
        cursor.execute("""
            SELECT id, nombre, tipo_especie, comentario
            FROM requerimientos
            WHERE usuario_id = %s
            ORDER BY nombre ASC
        """, (session['user_id'],))
        requerimientos = cursor.fetchall()
        
        print("📥 Datos de requerimientos obtenidos:", requerimientos)

        cursor.close()
        conn.close()
        
        return render_template('operaciones/requerimientos.html', requerimientos=requerimientos)
        
    except Exception as e:
        print("❌ Error al cargar requerimientos:", e)
        flash('Error al cargar los requerimientos. Por favor, inténtalo de nuevo.', 'danger')
        return redirect(url_for('panel'))

@app.route('/ver_requerimientos')
def ver_conjuntos_requerimientos():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para continuar.', 'error')
        return redirect(url_for('login'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # Selecciona todos los requerimientos registrados en la base de datos (sin filtrar por usuario)
        cursor.execute("""
            SELECT id, nombre, tipo_especie, comentario
            FROM requerimientos
        """)
        requerimientos = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('operaciones/ver_requerimientos.html', requerimientos=requerimientos)
    except Exception as e:
        print("❌ Error al cargar requerimientos:", e)
        flash("No se pudieron cargar los requerimientos", "danger")
        return redirect(url_for('panel'))

@app.route('/nuevo_requerimiento', methods=['GET', 'POST'])
def nuevo_requerimiento():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para crear requerimientos.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        nombre = request.form['nombre']
        tipo_especie = request.form['tipo_especie']
        comentario = request.form.get('comentario', '')
        usuario_id = session['user_id']

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO requerimientos (usuario_id, nombre, tipo_especie, comentario)
                VALUES (%s, %s, %s, %s)
            """, (usuario_id, nombre, tipo_especie, comentario))
            conn.commit()
            cursor.close()
            conn.close()

            flash('Requerimiento guardado exitosamente.', 'success')
            return redirect(url_for('requerimientos'))
        except Exception as e:
            print("❌ Error al guardar requerimiento:", e)
            flash('Error al guardar el requerimiento. Por favor, inténtalo de nuevo.', 'danger')
            return redirect(url_for('nuevo_requerimiento'))

    return render_template('operaciones/nuevo_requerimiento.html')


# Editar requerimiento
@app.route('/editar_requerimiento/<int:id>', methods=['GET', 'POST'])
def editar_requerimiento(id):
    if 'user_id' not in session:
        flash('Debes iniciar sesión para continuar.', 'error')
        return redirect(url_for('login'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if request.method == 'POST':
            nombre = request.form.get('nombre')
            tipo_especie = request.form.get('tipo_especie')
            comentario = request.form.get('comentario', '')
            
            cursor.execute("""
                UPDATE requerimientos 
                SET nombre=%s, tipo_especie=%s, comentario=%s 
                WHERE id=%s AND usuario_id=%s
            """, (nombre, tipo_especie, comentario, id, session['user_id']))
            
            if cursor.rowcount == 0:
                flash('No tienes permisos para editar este requerimiento.', 'error')
                cursor.close()
                conn.close()
                return redirect(url_for('requerimientos'))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Requerimiento actualizado correctamente.', 'success')
            return redirect(url_for('requerimientos'))

        # GET request - mostrar formulario de edición
        cursor.execute("""
            SELECT * FROM requerimientos 
            WHERE id = %s AND usuario_id = %s
        """, (id, session['user_id']))
        requerimiento = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not requerimiento:
            flash('Requerimiento no encontrado o sin permisos.', 'error')
            return redirect(url_for('requerimientos'))

        return render_template('operaciones/editar_requerimiento.html', requerimiento=requerimiento)
        
    except Exception as e:
        print("❌ Error al editar requerimiento:", e)
        flash('Error al procesar la solicitud. Por favor, inténtalo de nuevo.', 'danger')
        return redirect(url_for('requerimientos'))

# === Nueva ruta: guardar_nutrientes_requerimiento ===
@app.route('/guardar_nutrientes_requerimiento/<int:requerimiento_id>', methods=['POST'])
def guardar_nutrientes_requerimiento(requerimiento_id):
    if 'user_id' not in session:
        flash('Debes iniciar sesión para continuar.', 'error')
        return redirect(url_for('login'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Eliminar valores anteriores
        cursor.execute("DELETE FROM requerimientos_nutrientes WHERE requerimiento_id = %s", (requerimiento_id,))

        # Insertar nuevos valores desde el formulario
        for key, value in request.form.items():
            if key.startswith('valor_') and value.strip() != '':
                nutriente_id = int(key.replace('valor_', ''))
                valor = float(value)
                cursor.execute("""
                    INSERT INTO requerimientos_nutrientes (requerimiento_id, nutriente_id, valor)
                    VALUES (%s, %s, %s)
                """, (requerimiento_id, nutriente_id, valor))

        conn.commit()
        cursor.close()
        conn.close()

        flash('Valores de nutrientes guardados exitosamente.', 'success')
    except Exception as e:
        print("❌ Error al guardar nutrientes del requerimiento:", e)
        flash('Error al guardar los nutrientes del requerimiento.', 'danger')

    return redirect(url_for('editar_requerimiento', id=requerimiento_id))

# Eliminar requerimiento
@app.route('/eliminar_requerimiento/<int:id>')
def eliminar_requerimiento(id):
    if 'user_id' not in session:
        flash('Debes iniciar sesión para continuar.', 'error')
        return redirect(url_for('login'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM requerimientos 
            WHERE id = %s AND usuario_id = %s
        """, (id, session['user_id']))
        
        if cursor.rowcount == 0:
            flash('No tienes permisos para eliminar este requerimiento.', 'error')
        else:
            flash('Requerimiento eliminado correctamente.', 'success')
        
        conn.commit()
        cursor.close()
        conn.close()
        
    except Exception as e:
        print("❌ Error al eliminar requerimiento:", e)
        flash('Error al eliminar el requerimiento. Por favor, inténtalo de nuevo.', 'danger')

    return redirect(url_for('requerimientos'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)
    