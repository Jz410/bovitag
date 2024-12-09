from functools import wraps
from flask import session, redirect, url_for, flash

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_rango') != 'admin':
            flash("No tienes permiso para acceder a esta página.", "danger")
            return redirect(url_for('login.inicio'))
        return f(*args, **kwargs)
    return decorated_function


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Por favor, inicia sesión primero.", "warning")
            return redirect(url_for('login.inicio'))
        return f(*args, **kwargs)
    return decorated_function
