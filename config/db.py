import sqlite3
from functools import wraps

# Ruta de la base de datos
DATABASE = 'db/sqlite-tools-win-x64-3460100/Users'

# Función para obtener la conexión a la base de datos
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Esto permite acceder a las columnas por nombre
    return conn

# Función para inicializar la base de datos
def init_db():
    conn = get_db()
    c = conn.cursor()
    
    # Crear la tabla si no existe
    c.execute('''
        CREATE TABLE IF NOT EXISTS config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            output_folder TEXT NOT NULL,
            output_size_width INTEGER NOT NULL,
            output_size_height INTEGER NOT NULL
        )
    ''')
    
    # Insertar valores predeterminados si no hay registros
    c.execute('SELECT COUNT(*) FROM config')
    if c.fetchone()[0] == 0:
        c.execute('''
            INSERT INTO config (output_folder, output_size_width, output_size_height)
            VALUES (?, ?, ?)
        ''', ('', 497, 535))
    
    conn.commit()
    conn.close()

# Decorador para gestionar la conexión a la base de datos
def db_connection(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        conn = get_db()
        try:
            return func(conn, *args, **kwargs)
        finally:
            conn.close()
    return wrapper

# Función para cargar la configuración desde la base de datos
@db_connection
def load_config(conn):
    c = conn.cursor()
    c.execute('SELECT * FROM config ORDER BY id DESC LIMIT 1')
    config = c.fetchone()
    
    return {
        'output_folder': config['output_folder'] if config else '',
        'output_size_width': config['output_size_width'] if config else 497,
        'output_size_height': config['output_size_height'] if config else 535
    }

# Función para guardar la configuración en la base de datos
@db_connection
def save_config(conn, config):
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO config (output_folder, output_size_width, output_size_height)
        VALUES (?, ?, ?)
    ''', (config['output_folder'], config['output_size_width'], config['output_size_height']))
    
    conn.commit()
