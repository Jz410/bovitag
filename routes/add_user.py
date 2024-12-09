import pymysql
from werkzeug.security import generate_password_hash

def insertar_usuario(nombre, contraseña, rango):
    try:
        # Conexión a la base de datos
        conn = pymysql.connect(
            host='127.0.0.1',  # Cambia si usas otro host
            user='root',
            password='7003',
            database='bovitag1'
        )
        with conn.cursor() as cursor:
            # Generar hash de la contraseña
            hashed_password = generate_password_hash(contraseña)
            
            # Insertar usuario
            query = "INSERT INTO usuarios (nombre, contraseña, rango) VALUES (%s, %s, %s)"
            cursor.execute(query, (nombre, hashed_password, rango))
            
            conn.commit()
            print(f"Usuario '{nombre}' insertado correctamente.")
    except pymysql.Error as e:
        print(f"Error al insertar el usuario: {e}")
    finally:
        conn.close()

# Crear usuario inicial
insertar_usuario('admin', 'admin123', 'admin')  # Cambia los valores según necesites
