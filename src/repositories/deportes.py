from src.db import conexion


def listar_deportes():
    """
    Ejecuta la consulta SQL para conseguir la lista completa de deportes.

    Precondiciones:
        - La base de datos debe estar accesible.
    Postcondiciones:
        - Retorna una lista de diccionarios con las claves 'id' y 'nombre'.
        - Retorna una lista vacía [] si no existen registros en la tabla.
    """
    connection = conexion()
    # dictionary=True se encarga de mapear cada fila directamente a un diccionario de Python
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, nombre FROM deportes ORDER BY id ASC;")
        return cursor.fetchall()
    finally:
        # El bloque finally garantiza cerrar el cursor y la conexión ante cualquier escenario
        cursor.close()
        connection.close()