import sqlite3
from werkzeug.security import generate_password_hash

def hash(User:str, Password:str, Level:str):
    conn = sqlite3.connect('db/sqlite-tools-win-x64-3460100/Users')
    cursor = conn.cursor()

    username = User
    password = generate_password_hash(f'{Password}')
    rango = Level

    cursor.execute("INSERT INTO usuarios (nombre, contraseña, rango) VALUES (?, ?, ?)", (username, password, rango))
    conn.commit()
    conn.close()
    print("Usuario creado correctamente.")
