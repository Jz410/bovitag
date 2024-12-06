import os
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
 
import sqlite3

users_bp = Blueprint('users', __name__)

# Conexión a la base de datos
def get_db_connection():
    conn = sqlite3.connect('db/sqlite-tools-win-x64-3460100/Users')  
    conn.row_factory = sqlite3.Row
    return conn

@users_bp.route('/addusers', methods=['GET', 'POST'])
def usuarios():

    titulo:str = 'Añadir usuarios'

    if request.method == 'POST':
        usuario = request.form['nombre']
        password = request.form['contraseña']
        rango = request.form['rango']



        try:
            # Conexión a la base de datos
            conn = get_db_connection()
            cursor = conn.cursor()

            # Insertar los datos del usuario en la base de datos
            cursor.execute("INSERT INTO usuarios (nombre, contraseña, rango) VALUES (?, ?, ?)", 
                           (usuario, password, rango))
            
            # Guardar cambios
            conn.commit()

            flash('Usuario registrado exitosamente', 'success')

        except Exception as e:
            conn.rollback()  # Revertir cambios en caso de error
            flash(f'Ocurrió un error: {str(e)}', 'danger')
        
        finally:
            conn.close()

    return render_template('users.html',titulo=titulo)
