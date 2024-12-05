import sqlite3
from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from key import key
from routes.admin import admin_bp
from routes.generator import generator_bp, move_images_bp, files_bp, preview_bp
from routes.login import login_bp, inicio_bp
from routes.users import users_bp



app = Flask(__name__)
app.secret_key = key

# Registrar los blueprints
app.register_blueprint(admin_bp)
app.register_blueprint(generator_bp)
app.register_blueprint(files_bp)
app.register_blueprint(move_images_bp)
app.register_blueprint(preview_bp)
app.register_blueprint(login_bp)
app.register_blueprint(inicio_bp)
app.register_blueprint(users_bp)


if __name__ == "__main__":
    app.run(debug=True)
