import os
import cv2
import numpy as np
import base64
import sqlite3
from flask import Flask, render_template, request, redirect, session, flash, url_for, jsonify, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from key import key

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

# Funciones de configuración
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

@app.route('/')
def index():
    if 'user_id' not in session:
        flash("Debes iniciar sesión para acceder al Generador", "warning")
        return redirect('/login')
    return redirect('/generator')


@app.route('/login', methods=["POST", "GET"])
def login():
    titulo = 'Login'
    if request.method == "POST":
        user = request.form.get("user", "").strip()
        password = request.form.get("password", "").strip()

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

@app.route('/logout')
def logout():
    session.clear()
    flash("Sesión cerrada correctamente", "info")
    return redirect('/login')


@app.route('/generator', methods=['GET', 'POST'])
def generator():
    if 'user_id' not in session:
        flash("Debes iniciar sesión para acceder al Generador", "warning")
        return redirect('/login') 

    config = load_config()
    if request.method == 'POST':
        input_folder = request.form.get('input_folder')
        if not os.path.isdir(input_folder):
            flash("La carpeta ingresada no es válida", "danger")
            return redirect(url_for('generator'))

        start_number = int(request.form.get('start_number', 2701))
        output_folder = os.path.abspath(config['output_folder'])
        os.makedirs(output_folder, exist_ok=True)

        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        image_files = [f for f in os.listdir(input_folder)
                       if os.path.isfile(os.path.join(input_folder, f))
                       and os.path.splitext(f)[1].lower() in image_extensions]

        numero_actual = start_number
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
                    numero_actual += 1

            except Exception as e:
                flash(f"Error procesando {filename}: {e}", "danger")

        flash(f"Proceso completado. Imágenes guardadas en {output_folder}", "success")
        return redirect(url_for('generator'))

    return render_template('generator.html', config=config)

if __name__ == "__main__":
    app.run(debug=True)
