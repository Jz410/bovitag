import os
import cv2
import numpy as np
import time
from flask import Blueprint, render_template, request, send_file, session, flash, redirect, jsonify
from werkzeug.utils import secure_filename
from .config import load_config
from models.bdd import db_operation
from uuid import uuid4
import zipfile

# Blueprints
generator_bp = Blueprint('generator', __name__)
files_bp = Blueprint('files', __name__)

@files_bp.route('/list_files')
def list_files():
    folder = request.args.get('folder', '')
    if not os.path.isdir(folder):
        return jsonify([])

    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    image_files = [
        f for f in os.listdir(folder)
        if os.path.isfile(os.path.join(folder, f))
        and os.path.splitext(f)[1].lower() in image_extensions
    ]
    return jsonify(image_files)

@generator_bp.route('/generator', methods=['GET', 'POST'])
@db_operation
def generator(cursor):
    titulo = 'Generador de Imágenes'
    if 'user_id' not in session:
        flash("Debes iniciar sesión para acceder a esta página.", "warning")
        return redirect('/login')

    user_name = session.get('user_name', 'Usuario Desconocido')
    config = load_config()
    output_folder = os.path.abspath(config['output_folder'])
    os.makedirs(output_folder, exist_ok=True)

    if request.method == 'POST':
        numero_actual = int(request.form.get('start_number', 2701))
        uploaded_files = request.files.getlist('input_files')
        total_files = len(uploaded_files)
        session['progress'] = 0

        processed_count, skipped_count = 0, 0
        generated_images = []

        for index, uploaded_file in enumerate(uploaded_files):
            session['progress'] = int(((processed_count + skipped_count) / total_files) * 100)
            if uploaded_file and uploaded_file.filename:
                try:
                    if not uploaded_file.filename.lower().endswith(('jpg', 'jpeg', 'png')):
                        skipped_count += 1
                        continue

                    img_array = np.frombuffer(uploaded_file.read(), np.uint8)
                    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

                    if img is None:
                        skipped_count += 1
                        continue

                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
                    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                    if contours:
                        symbol_contour = max(contours, key=cv2.contourArea)
                        x, y, w, h = cv2.boundingRect(symbol_contour)
                        cropped = img[y:y+h, x:x+w]

                        output_size = (config['output_size_width'], config['output_size_height'])
                        resized = cv2.resize(cropped, output_size, interpolation=cv2.INTER_AREA)

                        nuevo_nombre = f"{numero_actual:04d}_{uuid4().hex[:6]}.jpg"
                        cv2.imwrite(os.path.join(output_folder, nuevo_nombre), resized)

                        cursor.execute(
                            "INSERT INTO registros (usuario_id, nombre_imagen) VALUES (%s, %s)",
                            (session['user_id'], nuevo_nombre)
                        )

                        generated_images.append(nuevo_nombre)
                        numero_actual += 1
                        processed_count += 1
                except Exception as e:
                    skipped_count += 1

            time.sleep(0.1)

        session['progress'] = 100
        return render_template('select_images.html', images=generated_images, output_folder=output_folder, user_name=user_name)

    return render_template('generator.html', config=config, titulo=titulo, user_name=user_name)

@generator_bp.route('/progress')
def progress():
    return jsonify(progress=session.get('progress', 0))

@generator_bp.route('/move_images', methods=['POST'])
@db_operation
def move_images(cursor):
    selected_images = request.form.getlist('selected_images')
    output_folder = request.form['output_folder']

    if not selected_images:
        selected_images = os.listdir(output_folder)

    zip_path = os.path.join(output_folder, 'imagenes.zip')
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for image in selected_images:
            image_path = os.path.join(output_folder, image)
            zipf.write(image_path, arcname=image)

    return send_file(zip_path, as_attachment=True)
