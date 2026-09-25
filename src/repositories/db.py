from sqlalchemy import create_engine, text
from src.constants import DB_URL
import mysql.connector
from src.constants import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

# Motor de conexión con pool automático
motor = create_engine(DB_URL, pool_pre_ping=True)

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

def fila_a_dict(fila) -> dict:
    """Convierte una fila del resultado en un diccionario."""
    return dict(fila._mapping)


def ejecutar_consulta(sql: str, parametros: dict = None) -> list[dict]:
    """Ejecuta un SELECT y devuelve una lista de diccionarios."""
    with motor.connect() as conexion:
        resultado = conexion.execute(text(sql), parametros or {})
        return [fila_a_dict(fila) for fila in resultado]


def ejecutar_mutacion(sql: str, parametros: dict = None) -> int:
    """Ejecuta INSERT, UPDATE o DELETE con commit automático.

    Retorna el ID autoincremental generado (o 0 si no aplica).
    """
    with motor.begin() as conexion:
        resultado = conexion.execute(text(sql), parametros or {})
        return resultado.lastrowid or 0