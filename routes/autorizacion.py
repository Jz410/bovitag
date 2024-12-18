import pymysql
from flask import Flask, render_template, request, redirect, session, flash, Blueprint, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from models.bdd import get_db_connection

autorizacion_bp = Blueprint('autorizacion', __name__)

@autorizacion_bp.route('/autorizacion', methods=["GET", "POST"])
def autorizacion():
    titulo = 'Autorizar usuarios'
    conn = get_db_connection()
    if not conn:
        flash("No se pudo conectar a la base de datos.", "danger")
        return render_template('generator.html')

    # Si es un POST request, manejar la habilitación/deshabilitación de usuarios
    if request.method == "POST":
        user_id = request.form.get('user_id')
        
        # Verificar si el user_id es válido
        if not user_id or not user_id.isdigit():
            flash("ID de usuario no proporcionado o no válido.", "danger")
            return redirect(url_for('autorizacion.autorizacion'))
        
        try:
            with conn.cursor() as cursor:
                # Obtener el estado actual de 'activo' del usuario
                query = "SELECT activo FROM usuarios WHERE id = %s"
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()
                
                if result is not None:  # Verificar si hay resultado
                    activo_actual = result.get('activo', None)  # Asegurarse de que 'activo' exista
                    if activo_actual is not None:
                        nuevo_estado = 0 if activo_actual == 1 else 1
                        update_query = "UPDATE usuarios SET activo = %s WHERE id = %s"
                        cursor.execute(update_query, (nuevo_estado, user_id))
                        conn.commit()
                        flash("Estado del usuario actualizado correctamente.", "success")
                    else:
                        flash("No se pudo obtener el estado actual del usuario.", "danger")
                else:
                    flash("Usuario no encontrado.", "danger")
        except pymysql.Error as e:
            flash(f"Error al actualizar el estado del usuario: {e}", "danger")
        finally:
            conn.close()  # Cerrar la conexión

        # Redirigir después del POST para evitar reenvío de formularios al actualizar la página
        return redirect(url_for('autorizacion.autorizacion'))

    # Recuperar el filtro de búsqueda (si existe)
    search_query = request.args.get('search', '')

    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            if search_query:
                # Si hay un filtro de búsqueda, ajustar la consulta SQL
                query = "SELECT id, nombre, rango, activo FROM usuarios WHERE nombre LIKE %s"
                cursor.execute(query, ('%' + search_query + '%',))
            else:
                # Recuperar todos los usuarios si no hay búsqueda
                query = "SELECT id, nombre, rango, activo FROM usuarios"
                cursor.execute(query)
            
            usuarios = cursor.fetchall()
        
        return render_template('administracion.html', 
                               usuarios=usuarios, 
                               titulo=titulo,
                               active_section='autorizacion')
    except pymysql.Error as e:
        flash(f"Error al consultar la base de datos: {e}", "danger")
        return render_template('error.html', error_message="Error al consultar la base de datos")
    finally:
        if conn:
            conn.close()  # Asegurarse de que la conexión se cierre correctamente
