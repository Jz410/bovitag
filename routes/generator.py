from flask import Blueprint, render_template, request, send_from_directory, session, flash, redirect
import sqlite3
import os
import cv2
import numpy as np
from werkzeug.utils import secure_filename
from .config import load_config

generator_bp = Blueprint('generator', __name__)
files_bp = Blueprint('files', __name__)
preview_bp = Blueprint('preview', __name__)
move_images_bp = Blueprint('move_images', __name__)
registro_bp = Blueprint('registro', __name__)

def get_db_connection():
    conn = sqlite3.connect('db/sqlite-tools-win-x64-3460100/Users')  # Asegúrate de que la ruta es correcta
    conn.row_factory = sqlite3.Row  # Para que las consultas devuelvan diccionarios
    return conn

@registro_bp.route('/image_log', methods=['GET'])
def image_log():
    conn = get_db_connection()

    # Asegúrate de que el campo 'user_id' es el correcto para la relación
    logs = conn.execute(
        'SELECT usuarios.nombre, image_log.image_name, image_log.timestamp '
        'FROM image_log '
        'JOIN usuarios ON image_log.id = usuarios.id '
        'ORDER BY image_log.timestamp DESC'
    ).fetchall()

    conn.close()  # Cerrar la conexión

    return render_template('registro.html', logs=logs)


@files_bp.route('/list_files')
def list_files():
    folder = request.args.get('folder', '')
    
    if not os.path.isdir(folder):
        return jsonify([])

    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    image_files = [
        f for f in os.listdir(folder)
        if os.path.isfile(os.path.join(folder, f)) and os.path.splitext(f)[1].lower() in image_extensions
    ]
    
    return jsonify(image_files)


@preview_bp.route('/get_image_preview/<path:filename>')
def get_image_preview(filename):
    folder = request.args.get('folder', '')
    full_path = os.path.join(folder, filename)
    
    if not os.path.isfile(full_path):
        return '', 404

    return send_from_directory(folder, filename)


@generator_bp.route('/generator', methods=['GET', 'POST'])
def generator():

    titulo:str = 'Generador de Imagenes'
    if 'user_id' not in session:
        flash("Debes iniciar sesión para generar imágenes.", "warning")
        return redirect('/login')

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
        image_files = [
            f for f in os.listdir(input_folder)
            if os.path.isfile(os.path.join(input_folder, f)) and os.path.splitext(f)[1].lower() in image_extensions
        ]
                
        for filename in image_files:
            try:
                img_path = os.path.join(input_folder, filename)
                img = cv2.imread(img_path)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                blurred = cv2.GaussianBlur(gray, (5, 5), 0)
                _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
                
                kernel = np.ones((3, 3), np.uint8)
                morph = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)
                contours, _ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                if contours:
                    symbol_contour = max(contours, key=cv2.contourArea)
                    mask = np.zeros_like(gray)
                    cv2.drawContours(mask, [symbol_contour], -1, 255, thickness=cv2.FILLED)
                    symbol = cv2.bitwise_and(img, img, mask=mask)
                    symbol[np.where(mask == 0)] = [255, 255, 255]
                    
                    x, y, w, h = cv2.boundingRect(symbol_contour)
                    symbol_cropped = symbol[y:y+h, x:x+w]
                    symbol_gray = cv2.cvtColor(symbol_cropped, cv2.COLOR_BGR2GRAY)
                    _, symbol_clean = cv2.threshold(symbol_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                    
                    symbol_final = np.ones_like(symbol_clean) * 255
                    symbol_final[symbol_clean == 0] = 0
                    output_size = (config['output_size_width'], config['output_size_height'])
                    symbol_resized = cv2.resize(symbol_final, output_size, interpolation=cv2.INTER_AREA)
                    
                    nuevo_nombre = f"{numero_actual:04d}.jpg"
                    output_path = os.path.join(output_folder, nuevo_nombre)
                    cv2.imwrite(output_path, symbol_resized)
                    
                    generated_images.append(nuevo_nombre)
                    numero_actual += 1
                    processed_count += 1
                else:
                    skipped_count += 1
            
            except Exception as e:
                flash(f"Error procesando {filename}: {e}", "danger")
        
        return render_template('select_images.html', images=generated_images, output_folder=output_folder)
    
    return render_template('generator.html', config=config, titulo=titulo)

@move_images_bp.route('/move_images', methods=['POST'])
def move_images():
    selected_images = request.form.getlist('selected_images')
    custom_folder = request.form.get('custom_folder')
    output_folder = request.form.get('output_folder')
    
    destination_folder = custom_folder if custom_folder else output_folder
    os.makedirs(destination_folder, exist_ok=True)

    for image_name in selected_images:
        src_path = os.path.join(output_folder, image_name)
        dest_path = os.path.join(destination_folder, image_name)
        os.rename(src_path, dest_path)

    flash("Imágenes movidas correctamente.", "success")
    return redirect('/generator')
