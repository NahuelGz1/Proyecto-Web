from src.repositories.db import ejecutar_consulta, ejecutar_mutacion
from src.utils import convertir_booleanos


# construye de forma dinamica la clausula WHERE y los parametros SQL segun los filtros especificados
# por ejemplo: {"id_cancha": 2, "estado": "confirmada"} -> ("WHERE id_cancha = :id_cancha AND estado = :estado", {...})
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

    if filtros.get("fecha"):
        condiciones.append("DATE(fecha_hora_inicio) = :fecha")
        parametros["fecha"] = filtros["fecha"]

    where_sql = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""
    return where_sql, parametros


# obtiene la cantidad total de reservas que coinciden con los filtros aplicados
# por ejemplo: retorna 15 para la cantidad total de reservas confirmadas de un socio
def contar_reservas(filtros: dict) -> int:
    where_sql, params = _armar_where(filtros)
    sql = f"SELECT COUNT(*) AS total FROM reservas {where_sql};"
    filas = ejecutar_consulta(sql, params)
    return filas[0]["total"] if filas else 0


# retorna el listado de reservas paginado y filtrado, ordenado por fecha de inicio descendente
# por ejemplo: devuelve hasta 10 reservas salteando las primeras 20
def listar_reservas(filtros: dict, limit: int, offset: int) -> list[dict]:
    where_sql, params = _armar_where(filtros)
    params["limit"] = limit
    params["offset"] = offset

    sql = f"""
        SELECT id, id_cancha, id_socio, fecha_hora_inicio, fecha_hora_fin, precio_total, estado
        FROM reservas
        {where_sql}
        ORDER BY fecha_hora_inicio DESC
        LIMIT :limit OFFSET :offset;
    """
    return ejecutar_consulta(sql, params)


# recupera la informacion completa de una reserva especifica buscando por su id
# por ejemplo: busca id=5 y convierte tipos booleanos en el resultado devuelto
def obtener_reserva_por_id(reserva_id: int) -> dict | None:
    sql = """
          SELECT id, id_cancha, id_socio, fecha_hora_inicio, fecha_hora_fin, precio_total, estado
          FROM reservas
          WHERE id = :reserva_id; \
          """
    filas = ejecutar_consulta(sql, {"reserva_id": reserva_id})
    if filas:
        return convertir_booleanos(filas)[0]
    return None


# verifica si existen reservas confirmadas que se solapen con el rango horario y cancha especificados
# por ejemplo: verifica disponibilidad ignorando la misma reserva durante una edicion (reserva_id_excluir)
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


# inserta un nuevo registro de reserva en la base de datos y retorna el id generado
# por ejemplo: crea una reserva 'confirmada' con fecha inicio, fin y montos
def crear_reserva(
        id_cancha,
        id_socio,
        fecha_hora_inicio,
        fecha_hora_fin,
        precio_total,
        estado="confirmada",
        precio_hora=None,
):
    if precio_hora is None:
        precio_hora = precio_total

    sql = """
          INSERT INTO reservas (id_cancha, id_socio, fecha_hora_inicio, fecha_hora_fin, precio_hora, precio_total, estado)
          VALUES (:id_cancha, :id_socio, :fecha_hora_inicio, :fecha_hora_fin, :precio_hora, :precio_total, :estado); \
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


# actualiza dinamicamente uno o mas campos de un registro de reserva existente
# por ejemplo: modifica los campos {"estado": "cancelada"} para el id correspondiente
def modificar_reserva(reserva_id: int, campos: dict) -> None:
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


# cambia el estado de una reserva a 'cancelada'
# por ejemplo: cancela la reserva invocando modificar_reserva(reserva_id, {"estado": "cancelada"})
def cancelar_reserva(reserva_id: int) -> None:
    modificar_reserva(reserva_id, {"estado": "cancelada"})


# elimina fisicamente el registro de una reserva de la base de datos segun su id
# por ejemplo: ejecuta DELETE FROM reservas WHERE id = 12
def eliminar_reserva(reserva_id: int) -> None:
    sql = "DELETE FROM reservas WHERE id = :reserva_id;"
    ejecutar_mutacion(sql, {"reserva_id": reserva_id})