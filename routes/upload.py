from werkzeug.security import generate_password_hash
import sqlite3
import os
import cv2
from flask import Blueprint, render_template, request, session, flash, redirect
from .config import load_config
from datetime import datetime

registro_bp = Blueprint('registro', __name__)

# Ruta para registrar imágenes
@registro_bp.route('/upload_image', methods=['GET', 'POST'])
def upload_image():
    if 'user_id' not in session:
        flash("Debes iniciar sesión para subir una imagen", "warning")
        return redirect('/login')
    
    if request.method == 'POST':
        # Obtener los datos del formulario
        usuario_id = session['user_id']  # El id del usuario logueado, desde la sesión
        image_file = request.files['image']
        image_name = image_file.filename
        
        if image_file:
            # Guardar la imagen en el directorio de salida
            config = load_config()
            output_folder = os.path.abspath(config['output_folder'])
            os.makedirs(output_folder, exist_ok=True)
            image_path = os.path.join(output_folder, image_name)
            image_file.save(image_path)
            
            # Insertar registro de la imagen en la base de datos
            conn = sqlite3.connect('mi_base_de_datos.db')
            cursor = conn.cursor()
            
            try:
                # Registrar la imagen en el log
                cursor.execute('''
                    INSERT INTO image_log (user_id, image_name, timestamp)
                    VALUES (?, ?, ?)
                ''', (usuario_id, image_name, datetime.now()))
                
                conn.commit()
                flash("Imagen subida y registrada correctamente", "success")
            except sqlite3.Error as e:
                flash(f"Error al registrar la imagen: {e}", "danger")
            finally:
                conn.close()

            return redirect('/image_log')  # Redirigir a la página donde se ve el historial de imágenes
        
    return render_template('upload_image.html')  # Página de formulario de subida de imagen
