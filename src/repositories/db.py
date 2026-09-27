from sqlalchemy import create_engine, text
from src.constants import DB_URL

# motor de conexion con pool automatico que verifica la validez de las conexiones antes de usarlas
motor = create_engine(DB_URL, pool_pre_ping=True)


# convierte un objeto de fila devuelto por sqlalchemy a un diccionario comun de python
# por ejemplo: convierte una fila de base de datos en {"id": 1, "nombre": "Juan"}
def fila_a_dict(fila) -> dict:
    return dict(fila._mapping)


# ejecuta consultas de lectura (SELECT) y devuelve los resultados como una lista de diccionarios
# por ejemplo: ejecutar_consulta("SELECT * FROM deportes WHERE id = :id", {"id": 1})
def ejecutar_consulta(sql: str, parametros: dict = None) -> list[dict]:
    with motor.connect() as conexion:
        resultado = conexion.execute(text(sql), parametros or {})
        return [fila_a_dict(fila) for fila in resultado]


# ejecuta escrituras (INSERT, UPDATE, DELETE) confirmando la transaccion automaticamente
# para INSERTs devuelve el id generado (ejemplo: 15); para UPDATE/DELETE o sin id devuelve 0
def ejecutar_mutacion(sql: str, parametros: dict = None) -> int:
    with motor.begin() as conexion:
        resultado = conexion.execute(text(sql), parametros or {})
        try:
            return resultado.lastrowid or 0
        except Exception:
            if resultado.returns_rows:
                fila = resultado.fetchone()
                return fila[0] if fila else 0
            return 0