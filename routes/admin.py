import os
from flask import Blueprint, render_template, request, redirect, url_for, session , flash
from .config import load_config, save_config 

# Definir el blueprint para la administración
admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin', methods=['GET', 'POST'])
def admin():

    titulo:str = 'Configuración de Imagenes'

    if 'user_id' not in session:
        flash("Debes iniciar sesión para ", "warning")
        return redirect('/login')
    config = load_config()  # Cargar la configuración
    
    if request.method == 'POST':
        # Obtener los valores del formulario
        config['output_folder'] = request.form.get('output_folder')
        config['output_size_width'] = int(request.form.get('output_size_width', 497))
        config['output_size_height'] = int(request.form.get('output_size_height', 535))
        
        # Asegurarse de que la carpeta de salida existe
        output_folder = os.path.abspath(config['output_folder'])
        os.makedirs(output_folder, exist_ok=True)
        
        # Guardar la configuración en la base de datos
        save_config(config)
        
        return redirect(url_for('generator.generator'))  # Redirigir al generador
    
    return render_template('admin.html', config=config,  titulo= titulo)
