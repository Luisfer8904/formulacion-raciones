from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.db import get_db_connection
from typing import Any

requerimientos_bp = Blueprint('requerimientos_bp', __name__)

@requerimientos_bp.route('/requerimientos')
def requerimientos():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para acceder.', 'error')
        return redirect(url_for('auth_bp.login'))
    
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
        return redirect(url_for('usuarios_bp.panel'))

@requerimientos_bp.route('/ver_requerimientos')
def ver_conjuntos_requerimientos():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para continuar.', 'error')
        return redirect(url_for('auth_bp.login'))

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
        return redirect(url_for('usuarios_bp.panel'))

@requerimientos_bp.route('/nuevo_requerimiento', methods=['GET', 'POST'])
def nuevo_requerimiento():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para crear requerimientos.', 'error')
        return redirect(url_for('auth_bp.login'))

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
            return redirect(url_for('requerimientos_bp.requerimientos'))
        except Exception as e:
            print("❌ Error al guardar requerimiento:", e)
            flash('Error al guardar el requerimiento. Por favor, inténtalo de nuevo.', 'danger')
            return redirect(url_for('requerimientos_bp.nuevo_requerimiento'))

    return render_template('operaciones/nuevo_requerimiento.html')

@requerimientos_bp.route('/editar_requerimiento/<int:id>', methods=['GET', 'POST'])
def editar_requerimiento(id):
    if 'user_id' not in session:
        flash('Debes iniciar sesión para continuar.', 'error')
        return redirect(url_for('auth_bp.login'))

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
                return redirect(url_for('requerimientos_bp.requerimientos'))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Requerimiento actualizado correctamente.', 'success')
            return redirect(url_for('requerimientos_bp.requerimientos'))

        # GET request - mostrar formulario de edición
        cursor.execute("""
            SELECT * FROM requerimientos 
            WHERE id = %s AND usuario_id = %s
        """, (id, session['user_id']))
        requerimiento: Any = cursor.fetchone()
        
        if not requerimiento:
            flash('Requerimiento no encontrado o sin permisos.', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('requerimientos_bp.requerimientos'))

        # Obtener nutrientes del usuario con sus valores actuales desde conjuntos_requerimientos
        cursor.execute("""
            SELECT n.id, n.nombre, n.unidad, n.tipo, cr.valor_sugerido
            FROM nutrientes n
            LEFT JOIN conjuntos_requerimientos cr ON n.id = cr.nutriente_id AND cr.requerimiento_id = %s
            WHERE n.usuario_id = %s
            ORDER BY n.nombre ASC
        """, (id, session['user_id']))
        nutrientes = cursor.fetchall()
        
        cursor.close()
        conn.close()

        return render_template('operaciones/editar_requerimiento.html', 
                             requerimiento=requerimiento, 
                             nutrientes=nutrientes)
        
    except Exception as e:
        print("❌ Error al editar requerimiento:", e)
        flash('Error al procesar la solicitud. Por favor, inténtalo de nuevo.', 'danger')
        return redirect(url_for('requerimientos_bp.requerimientos'))

@requerimientos_bp.route('/guardar_nutrientes_requerimiento/<int:requerimiento_id>', methods=['POST'])
def guardar_nutrientes_requerimiento(requerimiento_id):
    if 'user_id' not in session:
        flash('Debes iniciar sesión para continuar.', 'error')
        return redirect(url_for('auth_bp.login'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verificar que el requerimiento pertenece al usuario
        cursor.execute("SELECT id FROM requerimientos WHERE id = %s AND usuario_id = %s", 
                      (requerimiento_id, session['user_id']))
        if not cursor.fetchone():
            flash('No tienes permisos para editar este requerimiento.', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('requerimientos_bp.requerimientos'))

        # Eliminar valores anteriores de conjuntos_requerimientos
        cursor.execute("DELETE FROM conjuntos_requerimientos WHERE requerimiento_id = %s", (requerimiento_id,))

        # Insertar nuevos valores desde el formulario
        valores_guardados = 0
        for key, value in request.form.items():
            if key.startswith('valor_') and value.strip() != '':
                try:
                    nutriente_id = int(key.replace('valor_', ''))
                    valor_sugerido = float(value)
                    
                    # Verificar que el nutriente pertenece al usuario
                    cursor.execute("SELECT id FROM nutrientes WHERE id = %s AND usuario_id = %s", 
                                  (nutriente_id, session['user_id']))
                    if cursor.fetchone():
                        cursor.execute("""
                            INSERT INTO conjuntos_requerimientos (requerimiento_id, nutriente_id, valor_sugerido)
                            VALUES (%s, %s, %s)
                        """, (requerimiento_id, nutriente_id, valor_sugerido))
                        valores_guardados += 1
                except (ValueError, TypeError) as e:
                    print(f"❌ Error al procesar nutriente {key}: {e}")
                    continue

        conn.commit()
        cursor.close()
        conn.close()

        if valores_guardados > 0:
            flash(f'Se guardaron {valores_guardados} valores de nutrientes exitosamente.', 'success')
        else:
            flash('No se guardaron valores. Verifica que los valores sean números válidos.', 'warning')
            
    except Exception as e:
        print("❌ Error al guardar nutrientes del requerimiento:", e)
        flash('Error al guardar los nutrientes del requerimiento.', 'danger')

    return redirect(url_for('requerimientos_bp.editar_requerimiento', id=requerimiento_id))

@requerimientos_bp.route('/eliminar_requerimiento/<int:id>')
def eliminar_requerimiento(id):
    if 'user_id' not in session:
        flash('Debes iniciar sesión para continuar.', 'error')
        return redirect(url_for('auth_bp.login'))

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

    return redirect(url_for('requerimientos_bp.requerimientos'))
