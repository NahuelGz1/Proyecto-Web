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

    if filtros.get("fecha"):
        condiciones.append("DATE(fecha_hora_inicio) = :fecha")
        parametros["fecha"] = filtros["fecha"]

    where_sql = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""
    return where_sql, parametros


def contar_reservas(filtros: dict) -> int:
    where_sql, params = _armar_where(filtros)
    sql = f"SELECT COUNT(*) AS total FROM reservas {where_sql};"
    filas = ejecutar_consulta(sql, params)
    return filas[0]["total"] if filas else 0


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
    return convertir_booleanos(ejecutar_consulta(sql, params))


def obtener_reserva_por_id(reserva_id: int) -> dict | None:
    sql = """
          SELECT id, id_cancha, id_socio, fecha_hora_inicio, fecha_hora_fin, precio_total, estado
          FROM reservas
          WHERE id = :reserva_id; \
          """
    filas = ejecutar_consulta(sql, {"reserva_id": reserva_id})
    return convertir_booleanos(filas[0]) if filas else None


def existe_superposicion(id_cancha: int, inicio: str, fin: str, reserva_id_excluir: int = None) -> bool:
    """Verifica si existe alguna reserva confirmada para la misma cancha en esa franja horaria."""
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
        "fin": fin
    }

    if reserva_id_excluir:
        sql += " AND id != :reserva_id_excluir"
        params["reserva_id_excluir"] = reserva_id_excluir

    filas = ejecutar_consulta(sql, params)
    return len(filas) > 0


def crear_reserva(
        id_cancha: int,
        id_socio: int,
        fecha_hora_inicio: str,
        fecha_hora_fin: str,
        precio_total: float,
        estado: str = "confirmada"
) -> int:
    sql = """
          INSERT INTO reservas (id_cancha, id_socio, fecha_hora_inicio, fecha_hora_fin, precio_total, estado)
          VALUES (:id_cancha, :id_socio, :fecha_hora_inicio, :fecha_hora_fin, :precio_total, :estado); \
          """
    return ejecutar_mutacion(
        sql,
        {
            "id_cancha": id_cancha,
            "id_socio": id_socio,
            "fecha_hora_inicio": fecha_hora_inicio,
            "fecha_hora_fin": fecha_hora_fin,
            "precio_total": precio_total,
            "estado": estado,
        },
    )


def modificar_reserva(reserva_id: int, campos: dict) -> None:
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


def cancelar_reserva(reserva_id: int) -> None:
    sql = """
          UPDATE reservas
          SET estado = 'cancelada'
          WHERE id = :reserva_id; \
          """
    ejecutar_mutacion(sql, {"reserva_id": reserva_id})


def eliminar_reserva(reserva_id: int) -> None:
    sql = "DELETE FROM reservas WHERE id = :reserva_id;"
    ejecutar_mutacion(sql, {"reserva_id": reserva_id})