import pymysql
from werkzeug.security import generate_password_hash
import argparse

# Este código usar solo 1 vez y guardarlo en otro lado si es necesario

def insertar_usuario(nombre: str, contraseña: str, rango: str, activo: int):
    try:
        # Conexión a la base de datos Ejemplo
        conn = pymysql.connect(
            host='localhost',  # Cambia si usas otro host
            user='root',
            password='1234',
            database='bovitag1'
        )
        with conn.cursor() as cursor:
            # Generar hash de la contraseña
            hashed_password = generate_password_hash(contraseña)
            
            # Insertar usuario con el campo 'activo'
            query = "INSERT INTO usuarios (nombre, contraseña, rango, activo) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (nombre, hashed_password, rango, activo))
            
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
    parser.add_argument("activo", type=int, help="Estado del usuario: 1 para activo, 0 para inactivo.")

    # Parsear los argumentos
    args = parser.parse_args()

    # Llamar a la función con los argumentos proporcionados
    insertar_usuario(args.nombre, args.contraseña, args.rango, args.activo)


# python add_user.py "jairo" "1234" "admin" 1
