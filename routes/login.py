
import sqlite3
from flask import Flask, render_template, request, redirect, session, flash, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from key import key

login_bp = Blueprint('login', __name__)
inicio_bp = Blueprint('inicio', __name__)
# Funciones para la base de datos
def get_db_connection():
    conn = sqlite3.connect('db/sqlite-tools-win-x64-3460100/Users')
    conn.row_factory = sqlite3.Row
    return conn

def get_user_by_name(nombre):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM usuarios WHERE nombre = ?", (nombre,)).fetchone()
    conn.close()
    return user

@inicio_bp.route('/')
def index():
    return redirect('/login')

@login_bp.route('/login', methods=["POST", "GET"])
def inicio():

    titulo = 'Login'

    if request.method == "POST":
        user = request.form.get("user", "").strip()
        password = request.form.get("password", "").strip()

        # Validar usuario y contraseña
        usuario = get_user_by_name(user)
        if usuario and check_password_hash(usuario["contraseña"], password):
            session['user_id'] = usuario["id"]
            session['user_name'] = usuario["nombre"]
            session['user_rango'] = usuario["rango"]
            flash(f"¡Bienvenido, {usuario['nombre']}!", "success")
            return redirect('/generator')
        else:
            flash("Usuario o contraseña incorrectos", "danger")

    return render_template('login.html', titulo=titulo)

@login_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Debes iniciar sesión para acceder al dashboard", "warning")
        return redirect('/login')
    
    return f"¡Hola, {session['user_name']}! Eres {session['user_rango']}."

    return render_template('generator.html',titulo=titulo )

@login_bp.route('/logout')
def logout():
    session.clear()
    flash("Sesión cerrada correctamente", "info")
    return redirect('/login')
