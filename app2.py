import os
import cv2
import numpy as np
import base64
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
import sqlite3
from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from key import key

from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = key


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

@app.route('/login', methods=["POST", "GET"])
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


# Configuración por defecto
CONFIG_FILE = 'config.json'

def save_config(config):
    import json
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

def load_config():
    import json
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            'output_folder': '',
            'output_size_width': 497,
            'output_size_height': 535
        }

@app.route('/list_files')
def list_files():
    if 'user_id' not in session:
        flash("Debes iniciar sesión para acceder al dashboard", "warning")
        return redirect('/login')
    
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

@app.route('/get_image_preview/<path:filename>')
def get_image_preview(filename):
    if 'user_id' not in session:
        flash("Debes iniciar sesión para acceder al dashboard", "warning")
        return redirect('/login')
    
    folder = request.args.get('folder', '')
    
    # Construir la ruta completa
    full_path = os.path.join(folder, filename)
    
    # Validar si el archivo existe
    if not os.path.isfile(full_path):
        return '', 404

    # Devolver la imagen directamente desde el directorio
    return send_from_directory(folder, filename)

@app.route('/')
def index():
    if 'user_id' not in session:
        flash("Debes iniciar sesión para acceder al dashboard", "warning")
        return redirect('/login')
    return redirect(url_for('admin'))

init_db()

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    config = load_config()  # Cargar la configuración desde la base de datos
    
    if request.method == 'POST':
        # Obtener los valores del formulario
        config['output_folder'] = request.form.get('output_folder')
        config['output_size_width'] = int(request.form.get('output_size_width', 497))
        config['output_size_height'] = int(request.form.get('output_size_height', 535))
        
        # Asegurarse de que la carpeta de salida existe
        output_folder = os.path.abspath(config['output_folder'])  # Asegurar ruta absoluta
        os.makedirs(output_folder, exist_ok=True)
        
        # Guardar la configuración en la base de datos
        save_config(config)
        
        return redirect(url_for('generator'))
    
    return render_template('admin.html', config=config)

@app.route('/generator', methods=['GET', 'POST'])
def generator():
    config = load_config()  # Cargar la configuración desde la base de datos
    
    if request.method == 'POST':
        # Validar la carpeta de entrada
        input_folder = request.form.get('input_folder')
        if not os.path.isdir(input_folder):
            return f"Error: {input_folder} no es un directorio válido"
        
        start_number = int(request.form.get('start_number', 2701))
        
        # Asegurarse de que la carpeta de salida existe
        output_folder = os.path.abspath(config['output_folder'])  # Asegurar ruta absoluta
        os.makedirs(output_folder, exist_ok=True)
        
        # Procesar imágenes
        numero_actual = start_number
        processed_count = 0
        skipped_count = 0
        generated_images = []  # Lista de imágenes generadas para mostrar luego
        
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
                    
                    generated_images.append(nuevo_nombre)  # Añadir a la lista de generadas
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

@app.route('/move_images', methods=['POST'])
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
    
    return f"¡Imágenes movidas a {destination_folder}!"

if __name__ == '__main__':
    app.run(debug=True)