# image_processor/blueprints/admin_routes.py
import os
from flask import Blueprint, render_template, request, redirect, url_for

admin_bp = Blueprint('admin', __name__)

def save_config(config):
    import json
    with open('config.json', 'w') as f:
        json.dump(config, f)

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

@admin_bp.route('/', methods=['GET', 'POST'])
def index():
    config = load_config()
    
    if request.method == 'POST':
        # Actualizar configuración
        config['output_folder'] = request.form.get('output_folder')
        config['output_size_width'] = int(request.form.get('output_size_width', 497))
        config['output_size_height'] = int(request.form.get('output_size_height', 535))
        
        # Asegurarse de que la carpeta de salida existe
        output_folder = os.path.abspath(config['output_folder'])
        os.makedirs(output_folder, exist_ok=True)
        
        # Guardar configuración
        save_config(config)
        
        return redirect(url_for('generator.index'))
    
    return render_template('admin.html', config=config)