import os
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .config import load_config, save_config 
from routes.restriccion_de_rutas import admin_required
import logging

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin', methods=['GET', 'POST'])
@admin_required
def admin():
    titulo: str = 'Configuración de Imágenes'

    # Check if user is logged in
    if 'user_id' not in session:
        flash("Debes iniciar sesión para acceder", "warning")
        return redirect('/login')

    # Load existing configuration
    config = load_config()  
    
    if request.method == 'POST':
        try:
            # Validate and sanitize input
            output_folder = request.form.get('output_folder', '').strip()
            output_size_width = request.form.get('output_size_width', 497)
            output_size_height = request.form.get('output_size_height', 535)

            # Validate folder path
            if not output_folder:
                flash("La ruta de salida no puede estar vacía", "error")
                return render_template('administracion.html', config=config, titulo=titulo)

            # Validate image dimensions
            try:
                width = int(output_size_width)
                height = int(output_size_height)
                
                # Add reasonable dimension constraints
                if width <= 0 or height <= 0 or width > 4096 or height > 4096:
                    flash("Dimensiones de imagen inválidas", "error")
                    return render_template('administracion.html', config=config, titulo=titulo)
            
            except ValueError:
                flash("Las dimensiones deben ser números válidos", "error")
                return render_template('administracion.html', config=config, titulo=titulo)

            # Use absolute path and create directory if it doesn't exist
            output_folder = os.path.abspath(output_folder)
            
            try:
                os.makedirs(output_folder, exist_ok=True)
            except PermissionError:
                flash("No tienes permisos para crear esta carpeta", "error")
                return render_template('administracion.html', config=config, titulo=titulo)

            # Update configuration
            config['output_folder'] = output_folder
            config['output_size_width'] = width
            config['output_size_height'] = height
            
            # Save configuration
            save_config(config)
            
            # Log configuration change
            logging.info(f"Configuration updated: Folder {output_folder}, Size {width}x{height}")
            
            flash("Configuración guardada exitosamente", "success")
            return redirect(url_for('generator.generator'))

        except Exception as e:
            # Log any unexpected errors
            logging.error(f"Error updating configuration: {str(e)}")
            flash("Ocurrió un error al guardar la configuración", "error")
    
    return render_template('administracion.html', 
                           config=config, 
                           titulo=titulo, 
                           active_section='admin')

