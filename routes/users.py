from flask import Blueprint, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash
from models.bdd import get_db_connection  # Importa conexión MySQL desde el módulo correspondiente
from routes.restriccion_de_rutas import admin_required

users_bp = Blueprint('users', __name__)

@users_bp.route('/addusers', methods=['GET', 'POST'])
@admin_required
def usuarios():
    """
    Ruta para añadir usuarios a la base de datos MySQL.
    """
    titulo: str = 'Añadir usuarios'
    if 'user_id' not in session:
        flash("Debes iniciar sesión para ", "warning")
        return redirect('/login')

    if request.method == 'POST':
        # Obtener datos del formulario
        usuario = request.form['nombre'].strip()
        password = request.form['contraseña'].strip()
        rango = request.form['rango'].strip()

        try:
            # Conexión a la base de datos
            conn = get_db_connection()
            if not conn:
                flash("No se pudo conectar a la base de datos.", "danger")
                return render_template('users.html', titulo=titulo)

            with conn.cursor() as cursor:
                # Encriptar la contraseña
                hashed_password = generate_password_hash(password)

                # Insertar los datos en la tabla
                query = "INSERT INTO usuarios (nombre, contraseña, rango) VALUES (%s, %s, %s)"
                cursor.execute(query, (usuario, hashed_password, rango))

            # Guardar cambios en la base de datos
            conn.commit()
            flash('Usuario registrado exitosamente', 'success')

        except Exception as e:
            conn.rollback()  # Revertir cambios en caso de error
            flash(f'Ocurrió un error: {str(e)}', 'danger')

        finally:
            conn.close()

    return render_template('administracion.html', titulo=titulo)
