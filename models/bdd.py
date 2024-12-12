import pymysql
from pymysql.cursors import DictCursor
from functools import wraps
from flask import flash, redirect, url_for
from config.config import Config

def get_db_connection():
    try:
        conn = pymysql.connect(
            host=Config.DB_CONFIG['host'],
            user=Config.DB_CONFIG['user'],
            password=Config.DB_CONFIG['password'],
            database=Config.DB_CONFIG['database'],
            cursorclass=DictCursor
        )
        return conn
    except pymysql.Error as e:
        print(f"Error al conectar a la base de datos MySQL: {e}")
        return None

def db_operation(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        conn = get_db_connection()
        if not conn:
            flash("No se pudo conectar a la base de datos.", "danger")
            return redirect(url_for('generator.generator'))
        try:
            with conn.cursor() as cursor:
                result = func(cursor, *args, **kwargs)
            conn.commit()
            return result
        except pymysql.Error as e:
            conn.rollback()
            flash(f"Error en la base de datos: {e}", 'danger')
        finally:
            conn.close()
    return wrapper

