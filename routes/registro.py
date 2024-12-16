import os
import cv2
import numpy as np
from flask import Blueprint, render_template, request, send_from_directory, session, flash, redirect
from .config import load_config 
from routes.admin import admin_bp
from werkzeug.security import generate_password_hash, check_password_hash
from models.bdd import get_db_connection, db_operation
import time
from routes.restriccion_de_rutas import admin_required
import shutil
import zipfile
from flask import request, render_template, flash, send_file
from werkzeug.utils import secure_filename
from config.config import Config


registro_bp = Blueprint('registro', __name__)


@registro_bp.route('/image_processing_logs', methods=['GET'])
@admin_required
@db_operation
def image_processing_logs(cursor):
    titulo = 'Registro de procesamientos'
    if 'user_id' not in session:
        flash("Debes iniciar sesión para acceder", "warning")
        return redirect('/login')

    # Obtener el valor de búsqueda de los parámetros de consulta
    query = request.args.get('query', '').strip()

    # Construir la consulta SQL con filtro
    if query:
        cursor.execute("""
            SELECT r.id, r.nombre_imagen, r.fecha, r.usuario_nombre as usuario
            FROM registros r
            WHERE r.nombre_imagen LIKE %s
            ORDER BY r.fecha DESC
        """, (f"%{query}%",))
    else:
        cursor.execute("""
            SELECT r.id, r.nombre_imagen, r.fecha, r.usuario_nombre as usuario
            FROM registros r
            ORDER BY r.fecha DESC
        """)

    logs = cursor.fetchall()

    return render_template('administracion.html', logs=logs, 
                                                titulo=titulo, 
                                    active_section='image_processing_logs', 
                                    query=query)
