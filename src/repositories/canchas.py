from src.repositories.db import ejecutar_consulta, ejecutar_mutacion
from src.utils import convertir_booleanos


# construye dinamicamente los filtros SQL para listar o contar canchas
# por ejemplo: si le pasas {"id_deporte": 1, "techada": True}, genera 'WHERE id_deporte = :id_deporte AND techada = :techada'
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


# cuenta el total de canchas que coinciden con los filtros para la paginacion
# por ejemplo: devuelve 8 si hay 8 canchas techadas
def contar_canchas(filtros: dict) -> int:
    where_sql, params = _armar_where(filtros)
    sql = f"SELECT COUNT(*) AS total FROM canchas {where_sql};"
    filas = ejecutar_consulta(sql, params)
    return filas[0]["total"] if filas else 0


# trae la lista de canchas paginada y convierte los campos 0/1 (techada, activa) a booleanos
# por ejemplo: listar_canchas({}, limit=5, offset=0) trae las primeras 5 canchas
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
    return convertir_booleanos(ejecutar_consulta(sql, params))


# busca una cancha por su id unico
# por ejemplo: obtener_cancha_por_id(2) devuelve {"id": 2, "nombre": "Cancha 1", "techada": True, ...} o None
def obtener_cancha_por_id(cancha_id: int) -> dict | None:
    sql = """
          SELECT id, nombre, id_deporte, precio_hora, techada, activa
          FROM canchas
          WHERE id = :cancha_id; \
          """
    filas = ejecutar_consulta(sql, {"cancha_id": cancha_id})
    if filas:
        return convertir_booleanos(filas)[0]
    return None


# verifica si existe un deporte registrado con el id especificado
# por ejemplo: devuelve True si existe el deporte id=1 (Fútbol)
def existe_deporte(id_deporte: int) -> bool:
    sql = "SELECT id FROM deportes WHERE id = :id_deporte;"
    filas = ejecutar_consulta(sql, {"id_deporte": id_deporte})
    return len(filas) > 0


# inserta una nueva cancha en la base de datos y retorna el id asignado
# por ejemplo: crear_cancha("Cancha Central", 1, 1500, True, True) devuelve 5
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


# actualiza parcialmente los datos de una cancha segun los campos recibidos (PATCH)
# por ejemplo: si le pasas {"precio_hora": 2000}, actualiza solo el precio de esa cancha
def modificar_cancha(cancha_id: int, campos: dict) -> None:
    if not campos:
        return

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


# comprueba si la cancha tiene al menos una reserva vinculada (evita borrar canchas con historial)
# por ejemplo: devuelve True si la cancha id=3 ya fue reservada alguna vez
def tiene_reservas_asociadas(cancha_id: int) -> bool:
    sql = "SELECT COUNT(*) AS total FROM reservas WHERE id_cancha = :cancha_id;"
    filas = ejecutar_consulta(sql, {"cancha_id": cancha_id})
    return filas[0]["total"] > 0 if filas else False


# elimina fisicamente el registro de la cancha por su id
# por ejemplo: eliminar_cancha(4) borra la cancha id=4
def eliminar_cancha(cancha_id: int) -> None:
    sql = "DELETE FROM canchas WHERE id = :cancha_id;"
    ejecutar_mutacion(sql, {"cancha_id": cancha_id})


# funcion auxiliar para filtrar canchas activas que NO se solapen con reservas confirmadas en ese rango horario
# por ejemplo: excluye canchas reservadas entre las 18:00 y las 19:00 del 2026-03-30
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


# cuenta la cantidad total de canchas libres para la fecha, horario y filtros seleccionados
# por ejemplo: devuelve 3 si hay 3 canchas libres hoy de 18:00 a 19:00
def contar_canchas_disponibles(fecha: str, hora_inicio: str, hora_fin: str, filtros: dict) -> int:
    where_sql, params = _armar_where_disponibles(fecha, hora_inicio, hora_fin, filtros)
    sql = f"SELECT COUNT(*) AS total FROM canchas {where_sql};"
    filas = ejecutar_consulta(sql, params)
    return filas[0]["total"] if filas else 0


# devuelve la lista paginada de canchas disponibles en la fecha y rango horario indicados
# por ejemplo: devuelve las canchas libres de 18:00 a 19:00 formateando techada/activa como booleanos
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
    return convertir_booleanos(ejecutar_consulta(sql, params))