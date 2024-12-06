import sqlite3

# Conectar a la base de datos (se creará si no existe)
conn = sqlite3.connect('db/sqlite-tools-win-x64-3460100/Users')  # Asegúrate de que el nombre de la base de datos sea el correcto
cursor = conn.cursor()

# Crear la tabla de usuarios
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Crear la tabla de registro de imágenes
cursor.execute('''
CREATE TABLE IF NOT EXISTS image_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    image_name TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES usuarios(id) ON DELETE CASCADE
)
''')

# Confirmar cambios y cerrar conexión
conn.commit()
conn.close()

print("Tablas creadas correctamente.")
