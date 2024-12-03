# image_processor/blueprints/generator_routes.py
import os
import cv2
import numpy as np
from flask import Blueprint, render_template, request, jsonify, send_from_directory, flash, redirect, url_for

generator_bp = Blueprint('generator', __name__)

def load_config():
    import json
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            'output_folder': '',
            'output_size_width': 497,
            'output_size_height': 535
        }

@generator_bp.route('/', methods=['GET', 'POST'])
def index():
    config = load_config()
    
    if request.method == 'POST':
        # Validar la carpeta de entrada
        input_folder = request.form.get('input_folder')
        if not os.path.isdir(input_folder):
            return f"Error: {input_folder} no es un directorio válido"
        
        start_number = int(request.form.get('start_number', 2701))
        
        # Asegurarse de que la carpeta de salida existe
        output_folder = os.path.abspath(config['output_folder'])
        os.makedirs(output_folder, exist_ok=True)
        
        # Ruta del escritorio para imágenes no seleccionadas
        desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop', 'unselected_images')
        os.makedirs(desktop_path, exist_ok=True)
        
        # Procesar imágenes
        numero_actual = start_number
        processed_count = 0
        skipped_count = 0
        generated_images = []
        
        # Encontrar archivos de imagen
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        image_files = [
            f for f in os.listdir(input_folder) 
            if os.path.isfile(os.path.join(input_folder, f)) 
            and os.path.splitext(f)[1].lower() in image_extensions
        ]
        
        for filename in image_files:
            try:
                # Ruta completa de la imagen
                img_path = os.path.join(input_folder, filename)
                
                # Leer la imagen
                img = cv2.imread(img_path)
                
                # Convertir a escala de grises
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                
                # Aplicar desenfoque Gaussiano
                blurred = cv2.GaussianBlur(gray, (5, 5), 0)
                
                # Aplicar umbralización de Otsu
                _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
                
                # Operaciones morfológicas
                kernel = np.ones((3, 3), np.uint8)
                morph = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)
                
                # Encontrar contornos
                contours, _ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                if contours:
                    # Encontrar el contorno más grande
                    symbol_contour = max(contours, key=cv2.contourArea)
                    
                    # Crear una máscara y dibujar el contorno
                    mask = np.zeros_like(gray)
                    cv2.drawContours(mask, [symbol_contour], -1, 255, thickness=cv2.FILLED)
                    
                    # Aislar el símbolo
                    symbol = cv2.bitwise_and(img, img, mask=mask)
                    symbol[np.where(mask == 0)] = [255, 255, 255]
                    
                    # Recortar la imagen
                    x, y, w, h = cv2.boundingRect(symbol_contour)
                    symbol_cropped = symbol[y:y+h, x:x+w]
                    
                    # Convertir a escala de grises
                    symbol_gray = cv2.cvtColor(symbol_cropped, cv2.COLOR_BGR2GRAY)
                    
                    # Aplicar umbral fuerte
                    _, symbol_clean = cv2.threshold(symbol_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                    
                    # Crear imagen final del símbolo
                    symbol_final = np.ones_like(symbol_clean) * 255
                    symbol_final[symbol_clean == 0] = 0
                    
                    # Redimensionar
                    output_size = (config['output_size_width'], config['output_size_height'])
                    symbol_resized = cv2.resize(symbol_final, output_size, interpolation=cv2.INTER_AREA)
                    
                    # Guardar imagen procesada
                    nuevo_nombre = f"{numero_actual:04d}.jpg"
                    output_path = os.path.join(output_folder, nuevo_nombre)
                    cv2.imwrite(output_path, symbol_resized)
                    
                    generated_images.append(nuevo_nombre)
                    
                    numero_actual += 1
                    processed_count += 1
                else:
                    # Mover imagen no seleccionada al escritorio
                    desktop_output = os.path.join(desktop_path, filename)
                    os.rename(img_path, desktop_output)
                    skipped_count += 1
            
            except Exception as e:
                print(f"Error procesando {filename}: {e}")
        
        # Redirigir a la vista de las imágenes generadas
        return render_template('select_images.html', images=generated_images, output_folder=output_folder)
    
    return render_template('generator.html', config=config)

@generator_bp.route('/list_files')
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

@generator_bp.route('/get_image_preview/<path:filename>')
def get_image_preview(filename):
    folder = request.args.get('folder', '')
    
    # Construir la ruta completa
    full_path = os.path.join(folder, filename)
    
    # Validar si el archivo existe
    if not os.path.isfile(full_path):
        return '', 404

    # Devolver la imagen directamente desde el directorio
    return send_from_directory(folder, filename)


@generator_bp.route('/move_images', methods=['POST'])
def move_images():
    selected_images = request.form.getlist('selected_images')
    custom_folder = request.form.get('custom_folder')
    output_folder = request.form.get('output_folder')
    
    destination_folder = custom_folder if custom_folder else output_folder
    os.makedirs(destination_folder, exist_ok=True)
    
    # Mover imágenes seleccionadas
    for image_name in selected_images:
        src_path = os.path.join(output_folder, image_name)
        
        if not os.path.isfile(src_path):
            flash(f"Error: {image_name} no se encuentra en {output_folder}.")
            return redirect(url_for('generator_bp.generator'))  # Redirige al generador si hay un error
        
        dest_path = os.path.join(destination_folder, image_name)
        os.rename(src_path, dest_path)
    
    flash(f"¡Imágenes movidas a {destination_folder}!")
    return redirect(url_for('generator_bp.generator'))  # Redirigir después del éxito
