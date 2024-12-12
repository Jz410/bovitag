from werkzeug.security import generate_password_hash
from flask import flash, redirect, url_for

from models.bdd import  get_db_connection , db_operation


@db_operation
def create_user(cursor, username, password, rango):

    """
    Crea un usuario en la base de datos.

    :param cursor: Cursor de la base de datos (proporcionado automáticamente por el decorador).
    :param username: Nombre del usuario.
    :param password: Contraseña en texto plano (será encriptada).
    :param rango: Rango del usuario (e.g., 'user', 'admin').
    :return: Mensaje de éxito o error.
    """
    try:
        # Hash de la contraseña
        hashed_password = generate_password_hash(password)
        
        # Consulta SQL para insertar usuario
        query = "INSERT INTO usuarios (nombre, contraseña, rango) VALUES (%s, %s, %s)"
        values = (username, hashed_password, rango)
        
        # Ejecución de la consulta
        cursor.execute(query, values)
        flash("Usuario creado correctamente.", "success")
        return True
    except Exception as e:
        flash(f"Error al crear el usuario: {e}", "danger")
        return False

# Ejemplo de uso en un controlador Flask
def registrar_usuario():
    # Datos del usuario (pueden venir de un formulario, por ejemplo)
    username = 'jairo'
    password = '1234'
    rango = 'admin'

    # Crear usuario
    if create_user(username=username, password=password, rango=rango):
        return redirect(url_for('dashboard'))
    return redirect(url_for('registro'))
