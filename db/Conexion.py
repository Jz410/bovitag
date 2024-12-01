import mysql.connector 

def Coneccion(host = str,usuario = str,contraseña = str,nombre_base_datos = str): #hacer la conexion
    conexion = mysql.connector.connect(
        host = host,
        user = usuario,
        password = contraseña,
        database = nombre_base_datos)
    return conexion

def Cursor(conexion): #hacer el cursor para los comandos
    cursor = conexion.cursor()
    return cursor

def Consulta(comando = str,cursor = Cursor,conexion = Coneccion): #consulta de tablas o base de datos crear estos
    cursor.execute(comando)

def Insertar(nombre_tabla = str,cantidad_datos = str,datos = (),cursor = Cursor,conexion = Coneccion):#insertar datos usaremos un map o biblioteca
    #datos = (dato1,dato2,daton)
    comando = "insert into "+nombre_tabla+" values ("+cantidad_datos+");"
    cursor.execute(comando,datos)
    conexion.commit()

def ConsultaDatos(columnas = str,tabla = str,condicion = str,codigo_cond = str,cursor = Cursor): #consultar datos de cierta tabla
    comando = "select "+columnas+" from "+tabla+condicion+codigo_cond+";"
    date = []
    cursor.execute(comando)
    filas = cursor.fetchall()
    for f in filas:
        date.append(f)
    return date

def Imprimir(cursor = Cursor):
    imprimir = cursor.fetchall()
    for f in imprimir:
        print(f)

def ImprimirVariables(cursor = Cursor,variables = ()):
    imprimir = cursor.fetchall()
    for f in imprimir:
        print(f)
    for var in variables:
        print(var)


def Delete(tabla_o_variale = str,condicion = str,cond_a_cumplir = str,cursor = Cursor,conexion = Coneccion):
    comando = "delete from "+tabla_o_variale+condicion+cond_a_cumplir+";"
    cursor.execute(comando)
    conexion.commit()

def Update(tabla = str,columna = str,cambio = str,condicion = str,cond_a_cumplir = str,cursor = Cursor,conexion = Coneccion):
    comando = "update "+tabla+" set "+columna+" = "+cambio+condicion+cond_a_cumplir+";"
    cursor.execute(comando)
    conexion.commit()

def Cerrar(conexion = Coneccion): #cerrar la conexion
    conexion.close()