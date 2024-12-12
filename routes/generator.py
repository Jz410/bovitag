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


generator_bp = Blueprint('generator', __name__)
files_bp = Blueprint('files', __name__)


@files_bp.route('/list_files')
def list_files():
    folder = request.args.get('folder', '')
    
    # Validar si la carpeta existe
    if not os.path.isdir(folder):
        return jsonify([])
    
    # Extensiones de imagen para filtrar
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    
    # Obtener archivos de imagen
    image_files = [
        f for f in os.listdir(folder) 
        if os.path.isfile(os.path.join(folder, f)) 
        and os.path.splitext(f)[1].lower() in image_extensions
    ]
    
    return jsonify(image_files)


@generator_bp.route('/generator', methods=['GET', 'POST'])
@db_operation
def generator(cursor):
    titulo: str = 'Generador de imágenes'
    if 'user_id' not in session:
        flash("Debes iniciar sesión para ", "warning")
        return redirect('/login')

    # Get the user's name from the session
    user_name = session.get('user_name', 'Usuario Desconocido')
    config = load_config()
    
    if request.method == 'POST':
        output_folder = os.path.abspath(config['output_folder'])
        os.makedirs(output_folder, exist_ok=True)

        numero_actual = int(request.form.get('start_number', 2701))
        processed_count = 0
        skipped_count = 0
        generated_images = []
        
        # Get uploaded files directly from the request
        uploaded_files = request.files.getlist('input_files')
        
        # Debug: Log total number of uploaded files
        print(f"Total uploaded files: {len(uploaded_files)}")
        
        for uploaded_file in uploaded_files:
            if uploaded_file and uploaded_file.filename:
                try:
                    # Debug: Print filename being processed
                    print(f"Processing file: {uploaded_file.filename}")
                    
                    # Read the file directly from the uploaded file
                    img_array = np.frombuffer(uploaded_file.read(), np.uint8)
                    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                    
                    # Debug: Check if image was successfully read
                    if img is None:
                        print(f"Failed to decode image: {uploaded_file.filename}")
                        skipped_count += 1
                        continue

                    # Rest of the image processing
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

                    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

                    kernel = np.ones((3, 3), np.uint8)
                    morph = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)

                    contours, _ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                    if contours:
                        # Debug: Log number of contours found
                        print(f"Contours found in {uploaded_file.filename}: {len(contours)}")
                        
                        symbol_contour = max(contours, key=cv2.contourArea)

                        mask = np.zeros_like(gray)
                        cv2.drawContours(mask, [symbol_contour], -1, 255, thickness=cv2.FILLED)
                        symbol = cv2.bitwise_and(img, img, mask=mask)
                        symbol[np.where(mask == 0)] = [255, 255, 255]

                        x, y, w, h = cv2.boundingRect(symbol_contour)
                        symbol_cropped = symbol[y:y+h, x:x+w]
                        symbol_gray = cv2.cvtColor(symbol_cropped, cv2.COLOR_BGR2GRAY)
                        _, symbol_clean = cv2.threshold(symbol_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

                        padded = cv2.copyMakeBorder(symbol_clean, 200, 200, 200, 200, cv2.BORDER_CONSTANT, value=[255])
                        smoothed_edges = cv2.bilateralFilter(padded, 10, 95, 95)

                        output_size = (config['output_size_width'], config['output_size_height'])
                        symbol_resized = cv2.resize(smoothed_edges, output_size, interpolation=cv2.INTER_AREA)

                        nuevo_nombre = f"{numero_actual:04d}.jpg"
                        output_path = os.path.join(output_folder, nuevo_nombre)

                        # Debug: Print output path
                        print(f"Saving image to: {output_path}")
                        
                        cv2.imwrite(output_path, symbol_resized)

                        # Registrar en la base de datos
                        cursor.execute(
                            "INSERT INTO registros (usuario_id, nombre_imagen, usuario_nombre) VALUES (%s, %s, %s)",
                            (session['user_id'], nuevo_nombre, user_name)
                        )

                        generated_images.append(nuevo_nombre)
                        numero_actual += 1
                        processed_count += 1
                    else:
                        print(f"No contours found in {uploaded_file.filename}")
                        skipped_count += 1

                except Exception as e:
                    print(f"Error procesando {uploaded_file.filename}: {e}")
                    skipped_count += 1

        # Debug: Print processing summary
        print(f"Processing complete. Processed: {processed_count}, Skipped: {skipped_count}")

        return render_template('select_images.html', 
                               images=generated_images, 
                               output_folder=output_folder,
                               user_name=user_name)

    return render_template('generator.html', config=config, titulo=titulo, user_name=user_name)




