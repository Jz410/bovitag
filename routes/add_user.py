import pymysql
from werkzeug.security import generate_password_hash

def insertar_usuario(nombre:str, contraseña:str, rango:str):
    try:
        # Conexión a la base de datos
        conn = pymysql.connect(
            host='localhost',  # Cambia si usas otro host
            user='root',
            password='',
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
insertar_usuario('jairos', '1234', 'admin')  # Cambia los valores según necesites
