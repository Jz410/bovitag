import pymysql
from flask import Flask, render_template, request, redirect, session, flash, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from models.bdd import get_db_connection  

# Blueprints
login_bp = Blueprint('login', __name__)
inicio_bp = Blueprint('inicio', __name__)
auditoria_bp = Blueprint('auditoria', __name__)

def get_user_by_name(nombre):
    """
    Recupera un usuario por su nombre desde la base de datos MySQL si está activo.
    """
    conn = get_db_connection()
    if not conn:
        flash("No se pudo conectar a la base de datos.", "danger")
        return None

    try:
        with conn.cursor() as cursor:
            query = "SELECT * FROM usuarios WHERE nombre = %s AND activo = 1"
            cursor.execute(query, (nombre,))
            user = cursor.fetchone()
        return user
    except pymysql.Error as e:
        flash(f"Error al consultar la base de datos: {e}", "danger")
        return None
    finally:
        conn.close()


# Rutas
@inicio_bp.route('/')
def index():
    """
    Redirige a la página de inicio de sesión.
    """
    return redirect('/login')

@login_bp.route('/login', methods=["POST", "GET"])
def inicio():
    """
    Maneja la lógica de inicio de sesión.
    """
    titulo = 'Login'

    if request.method == "POST":
        user = request.form.get("user", "").strip()
        password = request.form.get("password", "").strip()

        # Validar usuario y contraseña
        usuario = get_user_by_name(user)
        if usuario:
            if check_password_hash(usuario["contraseña"], password):
                # Almacenar detalles del usuario en la sesión
                session['user_id'] = usuario["id"]
                session['user_name'] = usuario["nombre"]
                session['user_rango'] = usuario["rango"]
                flash(f"¡Bienvenido, {usuario['nombre']}!", "success")
                return redirect('/generator')
            else:
                flash("Contraseña incorrecta", "danger")
        else:
            flash("Usuario no encontrado o deshabilitado", "danger")

    return render_template('login.html', titulo=titulo)


@auditoria_bp.route('/auditoria/<int:user_id>', methods=["POST"])
def toggle_user(user_id):
    """
    Habilita o deshabilita un usuario.
    """
    conn = get_db_connection()
    if not conn:
        flash("No se pudo conectar a la base de datos.", "danger")
        return redirect('/auditoria')

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

    return redirect('/auditoria')  # Redirige al panel de auditoría

@auditoria_bp.route('/auditoria', methods=["GET"])

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
        return render_template('auditoria.html', usuarios=usuarios, titulo="Auditoría de Usuarios")
    except pymysql.Error as e:
        flash(f"Error al consultar la base de datos: {e}", "danger")
        return redirect('/')
    finally:
        conn.close()


@auditoria_bp.route('/gg')
def gg():
    return 'gg'
@login_bp.route('/logout')
def logout():
    """
    Maneja la lógica de cierre de sesión.
    """
    session.clear()
    flash("Sesión cerrada correctamente", "info")
    return redirect('/login')
