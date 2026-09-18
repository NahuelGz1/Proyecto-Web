import mysql.connector
from src.constants import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME


def conexion():
    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )


def obtener_cursor(connection):
    """Cursor centralizado: acá vive el dictionary=True, una sola vez."""
    return connection.cursor(dictionary=True)