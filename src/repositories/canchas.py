from src.repositories.db import ejecutar_consulta, ejecutar_mutacion
from src.utils import convertir_booleanos_cancha, convertir_booleanos_canchas


def _armar_where(filtros: dict):
    condiciones = []
    parametros = {}

    if filtros.get("id_deporte") is not None:
        condiciones.append("id_deporte = :id_deporte")
        parametros["id_deporte"] = filtros["id_deporte"]

    if filtros.get("nombre"):
        condiciones.append("nombre LIKE :nombre")
        parametros["nombre"] = f"%{filtros['nombre']}%"

    if filtros.get("techada") is not None:
        condiciones.append("techada = :techada")
        parametros["techada"] = filtros["techada"]

    if filtros.get("activa") is not None:
        condiciones.append("activa = :activa")
        parametros["activa"] = filtros["activa"]

    where_sql = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""
    return where_sql, parametros


def contar_canchas(filtros: dict) -> int:
    where_sql, params = _armar_where(filtros)
    sql = f"SELECT COUNT(*) AS total FROM canchas {where_sql};"
    filas = ejecutar_consulta(sql, params)
    return filas[0]["total"] if filas else 0


def listar_canchas(filtros: dict, limit: int, offset: int) -> list[dict]:
    where_sql, params = _armar_where(filtros)
    params["limit"] = limit
    params["offset"] = offset

    sql = f"""
        SELECT id, nombre, id_deporte, precio_hora, techada, activa
        FROM canchas
        {where_sql}
        ORDER BY id ASC
        LIMIT :limit OFFSET :offset;
    """
    return convertir_booleanos_canchas(ejecutar_consulta(sql, params))


def obtener_cancha_por_id(cancha_id: int) -> dict:
    sql = """
          SELECT id, nombre, id_deporte, precio_hora, techada, activa
          FROM canchas
          WHERE id = :cancha_id; \
          """
    filas = ejecutar_consulta(sql, {"cancha_id": cancha_id})
    return convertir_booleanos_cancha(filas[0]) if filas else None


def existe_deporte(id_deporte: int) -> bool:
    sql = "SELECT id FROM deportes WHERE id = :id_deporte;"
    filas = ejecutar_consulta(sql, {"id_deporte": id_deporte})
    return len(filas) > 0


def crear_cancha(
        nombre: str, id_deporte: int, precio_hora: int, techada: bool, activa: bool
) -> int:
    sql = """
          INSERT INTO canchas (nombre, id_deporte, precio_hora, techada, activa)
          VALUES (:nombre, :id_deporte, :precio_hora, :techada, :activa); \
          """
    return ejecutar_mutacion(
        sql,
        {
            "nombre": nombre,
            "id_deporte": id_deporte,
            "precio_hora": precio_hora,
            "techada": techada,
            "activa": activa,
        },
    )

# 23/9 ----------------------------------------------------------------------------------- (PATCH)
#utiliza el diccionario campos y crea una lista con los valores del mismo, la lista esta dividida por comas y en columnas
#esto arma el UPDATE y despues lo manda al set

def modificar_cancha(cancha_id: int, campos: dict) -> None:
    set_clauses = [f"{campo} = :{campo}" for campo in campos.keys()]
    set_sql = ", ".join(set_clauses)

    sql = f"""
        UPDATE canchas
        SET {set_sql}
        WHERE id = :cancha_id;
    """

    parametros = dict(campos)
    parametros["cancha_id"] = cancha_id

    ejecutar_mutacion(sql, parametros)


def tiene_reservas_asociadas(cancha_id: int) -> bool:
    sql = "SELECT COUNT(*) AS total FROM reservas WHERE id_cancha = :cancha_id;"
    filas = ejecutar_consulta(sql, {"cancha_id": cancha_id})
    return filas[0]["total"] > 0 if filas else False


def eliminar_cancha(cancha_id: int) -> None:
    sql = "DELETE FROM canchas WHERE id = :cancha_id;"
    ejecutar_mutacion(sql, {"cancha_id": cancha_id})




def _armar_where_disponibles(fecha, hora_inicio, hora_fin, filtros):
    condiciones = ["activa = 1"]
    parametros = {
        "inicio": f"{fecha} {hora_inicio}:00",
        "fin": f"{fecha} {hora_fin}:00",
    }

    if filtros.get("id_deporte") is not None:
        condiciones.append("id_deporte = :id_deporte")
        parametros["id_deporte"] = filtros["id_deporte"]

    if filtros.get("techada") is not None:
        condiciones.append("techada = :techada")
        parametros["techada"] = filtros["techada"]

    condiciones.append("""
        id NOT IN (
            SELECT id_cancha FROM reservas
            WHERE estado = 'confirmada'
              AND fecha_hora_inicio < :fin
              AND fecha_hora_fin > :inicio
        )
    """)

    where_sql = f"WHERE {' AND '.join(condiciones)}"
    return where_sql, parametros


def contar_canchas_disponibles(fecha: str, hora_inicio: str, hora_fin: str, filtros: dict) -> int:
    where_sql, params = _armar_where_disponibles(fecha, hora_inicio, hora_fin, filtros)
    sql = f"SELECT COUNT(*) AS total FROM canchas {where_sql};"
    filas = ejecutar_consulta(sql, params)
    return filas[0]["total"] if filas else 0


def listar_canchas_disponibles(fecha: str, hora_inicio: str, hora_fin: str, filtros: dict, limit: int, offset: int) -> list[dict]:
    where_sql, params = _armar_where_disponibles(fecha, hora_inicio, hora_fin, filtros)
    params["limit"] = limit
    params["offset"] = offset
    sql = f"""
        SELECT id, nombre, id_deporte, precio_hora, techada, activa
        FROM canchas
        {where_sql}
        ORDER BY id ASC
        LIMIT :limit OFFSET :offset;
    """
    return convertir_booleanos_canchas(ejecutar_consulta(sql, params))


