import os
import cv2
import numpy as np
import base64
import sqlite3
from flask import Flask, render_template, request, redirect, session, flash, url_for, jsonify, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from key import key
from routes.admin import admin_bp
from routes.generator import generator_bp, move_images_bp, files_bp, preview_bp
from routes.login import login_bp, inicio_bp
from routes.users import users_bp


app = Flask(__name__)
app.secret_key = key

#
app.register_blueprint(admin_bp)
app.register_blueprint(generator_bp)
app.register_blueprint(files_bp)
app.register_blueprint(move_images_bp)
app.register_blueprint(preview_bp)
app.register_blueprint(login_bp)
app.register_blueprint(inicio_bp)
app.register_blueprint(users_bp)

if __name__ == "__main__":
  app.run(debug=True,host='0.0.0.0', port=5000)
