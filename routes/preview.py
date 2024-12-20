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

move_images_bp = Blueprint('move_images', __name__)
preview_bp = Blueprint('preview', __name__)


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

@move_images_bp.route('/move_images', methods=['POST'])
def move_images():
    # Extract form data
    selected_images = request.form.getlist('selected_images')
    output_folder = request.form.get('output_folder')
    downloads_folder = os.path.expanduser('~/Downloads')  # Default downloads folder
   
    # Debug: Print out received paths
    print(f"Output Folder Path: {output_folder}")
    print(f"Selected Images: {selected_images}")
   
    # Prepare ZIP file path in downloads folder
    zip_filename = "imagenes_seleccionadas.zip"
    zip_filepath = os.path.join(downloads_folder, zip_filename)
   
    try:
        # Create ZIP file with selected images
        with zipfile.ZipFile(zip_filepath, 'w') as zipf:
            for image_name in selected_images:
                src_path = os.path.join(output_folder, image_name)
                if os.path.exists(src_path):
                    # Add the image to the ZIP file
                    zipf.write(src_path, arcname=secure_filename(image_name))
        
        # Attempt to remove images only if zip creation is successful
        for image_name in selected_images:
            src_path = os.path.join(output_folder, image_name)
            if os.path.exists(src_path):
                os.remove(src_path)

        # Send the ZIP file to the client
        return send_file(zip_filepath, as_attachment=True)
   
    except Exception as e:
        flash(f"Error al procesar las imágenes: {str(e)}", "error")
        return render_template('generator.html')