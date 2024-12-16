import pymysql
from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from werkzeug.security import generate_password_hash
from models.bdd import get_db_connection

# Create a blueprint for password-related routes
password_bp = Blueprint('password', __name__)

@password_bp.route('/cambiar_contrasena', methods=['GET', 'POST'])
def cambiar_contrasena():
    """
    Ruta para que un administrador cambie las contraseñas de los usuarios.
    """
    titulo = 'Gestión de Contraseñas'
    
    # Verificar si el usuario está logueado
    if 'user_id' not in session:
        flash("Debes iniciar sesión para acceder a esta función.", "warning")
        return redirect(url_for('login'))
    
    # Obtener la conexión a la base de datos
    conn = get_db_connection()
    if not conn:
        flash("No se pudo conectar a la base de datos.", "danger")
        return render_template('administracion.html', titulo=titulo)
    
    try:
        # Recuperar la lista de usuarios
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            query = "SELECT id, nombre, rango FROM usuarios"
            cursor.execute(query)
            usuarios = cursor.fetchall()
        
        # Manejar el cambio de contraseña si es un POST
        if request.method == 'POST':
            # Obtener los datos del formulario
            usuario_id = request.form.get('usuario_id')
            nueva_contraseña = request.form.get('nueva_contraseña', '').strip()
            
            # Validar los datos
            if not usuario_id or not nueva_contraseña:
                flash("Debe seleccionar un usuario y proporcionar una nueva contraseña.", "danger")
                return render_template('administracion.html', 
                                       titulo=titulo, 
                                       usuarios=usuarios,
                                       active_section='cambiar_contrasena')
            
            # Encriptar la nueva contraseña
            hashed_new_password = generate_password_hash(nueva_contraseña)
            
            # Actualizar la contraseña en la base de datos
            with conn.cursor() as cursor:
                update_query = "UPDATE usuarios SET contraseña = %s WHERE id = %s"
                cursor.execute(update_query, (hashed_new_password, usuario_id))
            
            # Confirmar los cambios
            conn.commit()
            flash('Contraseña actualizada exitosamente.', 'success')
            
            # Recargar los usuarios después de la actualización
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                query = "SELECT id, nombre, rango FROM usuarios"
                cursor.execute(query)
                usuarios = cursor.fetchall()
        
        return render_template('administracion.html', 
                               titulo=titulo, 
                               usuarios=usuarios,
                               active_section='cambiar_contrasena')
    
    except pymysql.Error as e:
        # Manejar cualquier error de base de datos
        conn.rollback()
        flash(f'Ocurrió un error: {str(e)}', 'danger')
        return render_template('administracion.html', 
                               titulo=titulo, 
                               active_section='cambiar_contrasena')
    
    finally:
        # Asegurar que la conexión se cierre
        conn.close()