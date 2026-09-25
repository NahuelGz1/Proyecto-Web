from sqlalchemy import create_engine, text
from src.constants import DB_URL

# Motor de conexión con pool automático
motor = create_engine(DB_URL, pool_pre_ping=True)


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