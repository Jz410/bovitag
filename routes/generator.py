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
generator_bp = Blueprint('generator', __name__)
files_bp = Blueprint('files', __name__)
preview_bp = Blueprint('preview', __name__)
move_images_bp = Blueprint('move_images', __name__)


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

@preview_bp.route('/get_image_preview/<path:filename>')
def get_image_preview(filename):
    folder = request.args.get('folder', '')
    
    # Construir la ruta completa
    full_path = os.path.join(folder, filename)
    
    # Validar si el archivo existe
    if not os.path.isfile(full_path):
        return '', 404

    # Devolver la imagen directamente desde el directorio
    return send_from_directory(folder, filename)

import os
import cv2
import numpy as np
from flask import session, flash, redirect, url_for, render_template, request
from config.config import Config

@generator_bp.route('/generator', methods=['GET', 'POST'])
@db_operation
def generator(cursor):
    titulo: str = 'Añadir usuarios'
    if 'user_id' not in session:
        flash("Debes iniciar sesión para ", "warning")
        return redirect('/login')

    # Get the user's name from the session
    user_name = session.get('user_name', 'Usuario Desconocido')
    config = load_config()
    
    if request.method == 'POST':
        input_folder = request.form.get('input_folder')
        if not os.path.isdir(input_folder):
            return f"Error: {input_folder} no es un directorio válido"

        start_number = int(request.form.get('start_number', 2701))
        output_folder = os.path.abspath(config['output_folder'])
        os.makedirs(output_folder, exist_ok=True)

        numero_actual = start_number
        processed_count = 0
        skipped_count = 0
        generated_images = []
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        
        # Image processing logic
        image_files = [
            f for f in os.listdir(input_folder) 
            if os.path.isfile(os.path.join(input_folder, f)) 
            and os.path.splitext(f)[1].lower() in image_extensions
        ]

        for filename in image_files:
            try:
                # Leer la imagen
                img_path = os.path.join(input_folder, filename)
                img = cv2.imread(img_path)

                # Convertir a escala de grises y suavizar
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                blurred = cv2.GaussianBlur(gray, (5, 5), 0)

                # Realizar umbralización
                _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

                # Operaciones morfológicas
                kernel = np.ones((3, 3), np.uint8)
                morph = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)

                # Encontrar contornos
                contours, _ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                if contours:
                    # Obtener el contorno más grande
                    symbol_contour = max(contours, key=cv2.contourArea)

                    # Crear una máscara y extraer el símbolo
                    mask = np.zeros_like(gray)
                    cv2.drawContours(mask, [symbol_contour], -1, 255, thickness=cv2.FILLED)
                    symbol = cv2.bitwise_and(img, img, mask=mask)
                    symbol[np.where(mask == 0)] = [255, 255, 255]

                    # Extraer y limpiar el símbolo
                    x, y, w, h = cv2.boundingRect(symbol_contour)
                    symbol_cropped = symbol[y:y+h, x:x+w]
                    symbol_gray = cv2.cvtColor(symbol_cropped, cv2.COLOR_BGR2GRAY)
                    _, symbol_clean = cv2.threshold(symbol_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

                    # Agregar padding blanco
                    padded = cv2.copyMakeBorder(symbol_clean, 200, 200, 200, 200, cv2.BORDER_CONSTANT, value=[255])

                    # Suavizar bordes
                    smoothed_edges = cv2.bilateralFilter(padded, 10, 95, 95)

                    # Redimensionar a las dimensiones configuradas
                    output_size = (config['output_size_width'], config['output_size_height'])
                    symbol_resized = cv2.resize(smoothed_edges, output_size, interpolation=cv2.INTER_AREA)

                    # Generar el nombre del archivo de salida
                    nuevo_nombre = f"{numero_actual:04d}.jpg"
                    output_path = os.path.join(output_folder, nuevo_nombre)

                    # Guardar la imagen procesada
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
                    skipped_count += 1

            except Exception as e:
                print(f"Error procesando {filename}: {e}")
                skipped_count += 1


        return render_template('select_images.html', 
                               images=generated_images, 
                               output_folder=output_folder,
                               user_name=user_name)

    return render_template('generator.html', config=config, titulo=titulo, user_name=user_name)



@generator_bp.route('/image_processing_logs')
@admin_required
@db_operation
def image_processing_logs(cursor):
    if 'user_id' not in session:
        flash("Debes iniciar sesión para acceder", "warning")
        return redirect('/login')

    # Fetch all logs, not filtered by user_id
    cursor.execute("""
        SELECT r.id, r.nombre_imagen, r.fecha, r.usuario_nombre as usuario 
        FROM registros r
        ORDER BY r.fecha DESC
    """)
    logs = cursor.fetchall()

    return render_template('image_processing_logs.html', logs=logs)


@move_images_bp.route('/move_images', methods=['POST'])
def move_images():
    selected_images = request.form.getlist('selected_images')
    custom_folder = request.form.get('custom_folder')
    output_folder = request.form.get('output_folder')
    
    # Usar la carpeta personalizada si se especifica, si no, usar la carpeta de salida
    destination_folder = custom_folder if custom_folder else output_folder
    
    os.makedirs(destination_folder, exist_ok=True)  # Crear carpeta si no existe
    
    # Mover imágenes seleccionadas
    for image_name in selected_images:
        src_path = os.path.join(output_folder, image_name)
        dest_path = os.path.join(destination_folder, image_name)
        os.rename(src_path, dest_path)
    
    return render_template('generator.html')