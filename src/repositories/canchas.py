from src.repositories.db import conexion, obtener_cursor


def _armar_where(filtros):
    condiciones = []
    parametros = []

    if filtros["id_deporte"] is not None:
        condiciones.append("id_deporte = %s")
        parametros.append(filtros["id_deporte"])

    if filtros["nombre"]:
        condiciones.append("nombre LIKE %s")
        parametros.append(f"%{filtros['nombre']}%")

    if filtros["techada"] is not None:
        condiciones.append("techada = %s")
        parametros.append(filtros["techada"])

    if filtros["activa"] is not None:
        condiciones.append("activa = %s")
        parametros.append(filtros["activa"])

    where_sql = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""
    return where_sql, parametros


def contar_canchas(filtros):
    where_sql, params = _armar_where(filtros)
    connection = conexion()
    cursor = obtener_cursor(connection)
    try:
        cursor.execute(f"SELECT COUNT(*) AS total FROM canchas {where_sql};", tuple(params))
        resultado = cursor.fetchone()
        return resultado["total"]
    finally:
        cursor.close()
        connection.close()


def listar_canchas(filtros, limit, offset):
    where_sql, params = _armar_where(filtros)
    connection = conexion()
    cursor = obtener_cursor(connection)
    try:
        query = f"""
            SELECT id, nombre, id_deporte, precio_hora, techada, activa
            FROM canchas
            {where_sql}
            ORDER BY id ASC
            LIMIT %s OFFSET %s;
        """
        cursor.execute(query, tuple(params) + (limit, offset))
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


def obtener_cancha_por_id(cancha_id):
    connection = conexion()
    cursor = obtener_cursor(connection)
    try:
        cursor.execute(
            "SELECT id, nombre, id_deporte, precio_hora, techada, activa FROM canchas WHERE id = %s;",
            (cancha_id,)
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        connection.close()

def existe_deporte(id_deporte):
    connection = conexion()
    cursor = obtener_cursor(connection)
    try:
        cursor.execute("SELECT id FROM deportes WHERE id = %s;", (id_deporte,))
        return cursor.fetchone() is not None
    finally:
        cursor.close()
        connection.close()

def crear_cancha(datos):
    connection = conexion()
    cursor = obtener_cursor(connection)
    try:
        query = """
            INSERT INTO canchas (nombre, id_deporte, precio_hora, techada, activa)
            VALUES (%s, %s, %s, %s, %s);
        """
        cursor.execute(query, (
            datos["nombre"],
            datos["id_deporte"],
            datos["precio_hora"],
            datos["techada"],
            datos["activa"],
        ))
        connection.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        connection.close()

def registrar_cancha():
    return


def existe_deporte(id_deporte: int) -> bool:
    connection = conexion()
    cursor = obtener_cursor(connection)
    try:
        cursor.execute("SELECT id FROM deportes WHERE id = %s;", (id_deporte,))
        return cursor.fetchone() is not None
    finally:
        cursor.close()
        connection.close()


def crear_cancha(
    nombre: str, id_deporte: int, precio_hora: int, techada: bool, activa: bool
) -> int:
    connection = conexion()
    cursor = obtener_cursor(connection)
    try:
        query = """
            INSERT INTO canchas (nombre, id_deporte, precio_hora, techada, activa)
            VALUES (%s, %s, %s, %s, %s);
        """
        cursor.execute(query, (
            nombre,
            id_deporte,
            precio_hora,
            techada,
            activa,
        ))
        connection.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        connection.close()
        

def modificar_cancha(cancha_id: int, campos: dict) -> None:
    pass


def tiene_reservas_asociadas(cancha_id: int) -> bool:
    pass


def eliminar_cancha(cancha_id: int) -> None:
    pass


def contar_canchas_disponibles(
        fecha: str, hora_inicio: str, hora_fin: str, filtros: dict
) -> int:
    pass


def listar_canchas_disponibles(
        fecha: str,
        hora_inicio: str,
        hora_fin: str,
        filtros: dict,
        limit: int,
        offset: int,
) -> list[dict]:
    pass



