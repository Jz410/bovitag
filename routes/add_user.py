import pymysql
from werkzeug.security import generate_password_hash
import argparse

def insertar_usuario(nombre: str, contraseña: str, rango: str):
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

if __name__ == "__main__":
    # Configurar el parser de argumentos
    parser = argparse.ArgumentParser(description="Agregar un usuario a la base de datos.")
    parser.add_argument("nombre", type=str, help="El nombre del usuario.")
    parser.add_argument("contraseña", type=str, help="La contraseña del usuario.")
    parser.add_argument("rango", type=str, help="El rango del usuario.")

    # Parsear los argumentos
    args = parser.parse_args()

    # Llamar a la función con los argumentos proporcionados
    insertar_usuario(args.nombre, args.contraseña, args.rango)


# python add_user.py "jairo" "1234" "admin"     // asi es como se llamaría desde terminal
