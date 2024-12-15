import pymysql
from flask import Flask, render_template, request, redirect, session, flash, Blueprint, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from models.bdd import get_db_connection  

autorizacion_bp = Blueprint('autorizacion', __name__)

@autorizacion_bp.route('/autorizacion', methods=["GET", "POST"])
def autorizacion():
    titulo: str = 'Autorizar usuarios'
    """
    Mostrar la lista de usuarios y permitir activar o desactivar usuarios.
    """
    
    conn = get_db_connection()
    if not conn:
        flash("No se pudo conectar a la base de datos.", "danger")
        return render_template('index.html')  # O la vista principal si no hay conexión a la DB
    
    if request.method == "POST":
        # Este bloque maneja la actualización del estado del usuario
        user_id = request.form.get('user_id')
        if not user_id:
            flash("ID de usuario no proporcionado.", "danger")
            return redirect(url_for('autorizacion.autorizacion'))
        
        try:
            with conn.cursor() as cursor:
                # Toggle the user's active status
                query = "UPDATE usuarios SET activo = NOT activo WHERE id = %s"
                cursor.execute(query, (user_id,))
                conn.commit()
            flash("Estado del usuario actualizado correctamente.", "success")
        except pymysql.Error as e:
            flash(f"Error al actualizar el estado del usuario: {e}", "danger")
        
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # Retrieve all users with their status
            query = "SELECT id, nombre, rango, activo FROM usuarios"
            cursor.execute(query)
            usuarios = cursor.fetchall()
        
        return render_template('administracion.html', 
                               usuarios=usuarios, 
                               titulo=titulo,
                               active_section='autorizacion')  # Se pasa 'toggle_user' como active_section
    except pymysql.Error as e:
        flash(f"Error al consultar la base de datos: {e}", "danger")
        return render_template('error.html', error_message="Error al consultar la base de datos")  # O cualquier página de error
    finally:
        conn.close()
