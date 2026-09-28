from src.repositories.db import ejecutar_consulta, ejecutar_mutacion
from src.utils import convertir_booleanos


def _armar_where(filtros: dict):
    condiciones = []
    parametros = {}

    if filtros.get("id_cancha") is not None:
        condiciones.append("id_cancha = :id_cancha")
        parametros["id_cancha"] = filtros["id_cancha"]

    if filtros.get("id_socio") is not None:
        condiciones.append("id_socio = :id_socio")
        parametros["id_socio"] = filtros["id_socio"]

    if filtros.get("estado"):
        condiciones.append("estado = :estado")
        parametros["estado"] = filtros["estado"]

    if filtros.get("fecha_desde"):
        condiciones.append("DATE(fecha_hora_inicio) >= :fecha_desde")
        parametros["fecha_desde"] = filtros["fecha_desde"]

    if filtros.get("fecha_hasta"):
        condiciones.append("DATE(fecha_hora_inicio) <= :fecha_hasta")
        parametros["fecha_hasta"] = filtros["fecha_hasta"]

    where_sql = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""
    return where_sql, parametros


def contar_reservas(filtros: dict) -> int:
    where_sql, params = _armar_where(filtros)
    sql = f"SELECT COUNT(*) AS total FROM reservas {where_sql};"
    filas = ejecutar_consulta(sql, params)
    return filas[0]["total"] if filas else 0


def listar_reservas(filtros: dict, limit: int, offset: int) -> list[dict]:
    where_sql, params = _armar_where(filtros)
    params_query = dict(params)
    params_query["limit"] = limit
    params_query["offset"] = offset

    sql = f"""
        SELECT id, id_cancha, id_socio, fecha_hora_inicio, fecha_hora_fin,
               precio_hora, precio_total, estado
        FROM reservas
        {where_sql}
        ORDER BY fecha_hora_inicio DESC
        LIMIT :limit OFFSET :offset;
    """
    filas = ejecutar_consulta(sql, params_query)
    return convertir_booleanos(filas)


def obtener_todas(filtros: dict, limit: int, offset: int) -> tuple[list[dict], int]:
    reservas = listar_reservas(filtros, limit, offset)
    total = contar_reservas(filtros)
    return reservas, total


def obtener_reserva_por_id(reserva_id: int) -> dict | None:
    sql = """
          SELECT id, id_cancha, id_socio, fecha_hora_inicio, fecha_hora_fin,
                 precio_hora, precio_total, estado
          FROM reservas
          WHERE id = :reserva_id; \
          """
    filas = ejecutar_consulta(sql, {"reserva_id": reserva_id})
    if filas:
        return convertir_booleanos(filas)[0]
    return None


def obtener_por_id(reserva_id: int) -> dict | None:
    return obtener_reserva_por_id(reserva_id)


def existe_superposicion(
        id_cancha: int, inicio: str, fin: str, reserva_id_excluir: int = None
) -> bool:
    sql = """
          SELECT id FROM reservas
          WHERE id_cancha = :id_cancha
            AND estado = 'confirmada'
            AND fecha_hora_inicio < :fin
            AND fecha_hora_fin > :inicio \
          """
    params = {
        "id_cancha": id_cancha,
        "inicio": inicio,
        "fin": fin,
    }

    if reserva_id_excluir:
        sql += " AND id != :reserva_id_excluir"
        params["reserva_id_excluir"] = reserva_id_excluir

    filas = ejecutar_consulta(sql, params)
    return len(filas) > 0


def verificar_solapamiento(
        id_cancha: int, fecha_hora_inicio: str, fecha_hora_fin: str, id_reserva_excluir: int = None
) -> bool:
    return existe_superposicion(id_cancha, fecha_hora_inicio, fecha_hora_fin, id_reserva_excluir)


def existe_socio(id_socio: int) -> bool:
    sql = "SELECT id, nombre, email, activo FROM socios WHERE id = :id_socio;"
    filas = ejecutar_consulta(sql, {"id_socio": id_socio})
    if filas:
        return convertir_booleanos(filas)[0]
    return None


def existe_cancha(id_cancha: int) -> bool:
    sql = "SELECT id, nombre, id_deporte, precio_hora, techada, activa FROM canchas WHERE id = :id_cancha;"
    filas = ejecutar_consulta(sql, {"id_cancha": id_cancha})
    if filas:
        return convertir_booleanos(filas)[0]
    return None

def obtener_estado_socio(id_socio: int) -> dict | None:
    sql = "SELECT id, activo FROM socios WHERE id = :id_socio;"
    filas = ejecutar_consulta(sql, {"id_socio": id_socio})
    return convertir_booleanos(filas)[0] if filas else None


def obtener_estado_cancha(id_cancha: int) -> dict | None:
    sql = "SELECT id, activa FROM canchas WHERE id = :id_cancha;"
    filas = ejecutar_consulta(sql, {"id_cancha": id_cancha})
    return convertir_booleanos(filas)[0] if filas else None


def crear_reserva(
        id_cancha: int,
        id_socio: int,
        fecha_hora_inicio: str,
        fecha_hora_fin: str,
        precio_hora: float = 0.0,
        precio_total: float = 0.0,
        estado: str = "confirmada",
) -> int:
    sql = """
          INSERT INTO reservas (
              id_cancha, id_socio, fecha_hora_inicio, fecha_hora_fin,
              precio_hora, precio_total, estado
          )
          VALUES (
                     :id_cancha, :id_socio, :fecha_hora_inicio, :fecha_hora_fin,
                     :precio_hora, :precio_total, :estado
                 ); \
          """
    parametros = {
        "id_cancha": id_cancha,
        "id_socio": id_socio,
        "fecha_hora_inicio": fecha_hora_inicio,
        "fecha_hora_fin": fecha_hora_fin,
        "precio_hora": precio_hora,
        "precio_total": precio_total,
        "estado": estado,
    }
    return ejecutar_mutacion(sql, parametros)


def crear(datos: dict) -> dict:
    nuevo_id = crear_reserva(
        id_cancha=datos["id_cancha"],
        id_socio=datos["id_socio"],
        fecha_hora_inicio=datos["fecha_hora_inicio"],
        fecha_hora_fin=datos["fecha_hora_fin"],
        precio_hora=datos.get("precio_hora", 0.0),
        precio_total=datos.get("precio_total", 0.0),
        estado=datos.get("estado", "confirmada"),
    )
    return obtener_por_id(nuevo_id)


def actualizar_reserva(reserva_id: int, campos: dict) -> None:
    if not campos:
        return

    set_clauses = [f"{campo} = :{campo}" for campo in campos.keys()]
    set_sql = ", ".join(set_clauses)

    sql = f"""
        UPDATE reservas
        SET {set_sql}
        WHERE id = :reserva_id;
    """

    parametros = dict(campos)
    parametros["reserva_id"] = reserva_id

    ejecutar_mutacion(sql, parametros)


def actualizar(id_reserva: int, datos: dict) -> dict:
    actualizar_reserva(id_reserva, datos)
    return obtener_por_id(id_reserva)


def actualizar_estado(id_reserva: int, nuevo_estado: str) -> dict:
    return actualizar(id_reserva, {"estado": nuevo_estado})


def cancelar_reserva(reserva_id: int) -> None:
    actualizar_reserva(reserva_id, {"estado": "cancelada"})


def eliminar_reserva(reserva_id: int) -> None:
    sql = "DELETE FROM reservas WHERE id = :reserva_id;"
    ejecutar_mutacion(sql, {"reserva_id": reserva_id})