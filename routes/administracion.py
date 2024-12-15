from flask import Flask, render_template, request, flash, url_for, Blueprint


administracion_bp = Blueprint('administracion', __name__)

@administracion_bp.route('/administracion')
def administracion():
    return render_template('administracion.html')
