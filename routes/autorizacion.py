import pymysql
from flask import Flask, render_template, request, redirect, session, flash, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from models.bdd import get_db_connection  

autorizacion_bp = Blueprint('autorizacion', __name__)

@autorizacion_bp.route('/autorizacion/<int:user_id>', methods=["POST"])
def toggle_user(user_id):
    """
    Habilita o deshabilita un usuario.
    """
    conn = get_db_connection()
    if not conn:
        flash("No se pudo conectar a la base de datos.", "danger")
        return redirect('/autorizacion')

    try:
        with conn.cursor() as cursor:
            # Cambiar el estado activo del usuario
            query = "UPDATE usuarios SET activo = NOT activo WHERE id = %s"
            cursor.execute(query, (user_id,))
            conn.commit()
        flash("Estado del usuario actualizado correctamente.", "success")
    except pymysql.Error as e:
        flash(f"Error al actualizar el estado del usuario: {e}", "danger")
    finally:
        conn.close()

    return redirect('/autorizacion')  # Redirige al panel de auditoría

@autorizacion_bp.route('/autorizacion', methods=["GET"])

def auditoria():
    """
    Muestra la lista de usuarios para auditoría.
    """
    conn = get_db_connection()
    if not conn:
        flash("No se pudo conectar a la base de datos.", "danger")
        return redirect('/')

    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # Recuperar todos los usuarios con sus estados
            query = "SELECT id, nombre, rango, activo FROM usuarios"
            cursor.execute(query)
            usuarios = cursor.fetchall()
        return render_template('autorizacion.html', usuarios=usuarios, titulo="Auditoría de Usuarios")
    except pymysql.Error as e:
        flash(f"Error al consultar la base de datos: {e}", "danger")
        return redirect('/')
    finally:
        conn.close()
