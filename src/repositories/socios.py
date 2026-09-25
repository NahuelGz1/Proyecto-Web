from src.repositories.db import ejecutar_consulta
from src.utils import convertir_booleanos

def listar_socios(nombre: str, activo: bool, limit: int, offset: int):
    condiciones = []
    parametros = {}

    if nombre:
        condiciones.append("nombre LIKE :nombre")
        parametros["nombre"] = f"%{nombre}%"

    if activo is not None:
        condiciones.append("activo = :activo")
        parametros["activo"] = activo

    where = "WHERE " + " AND ".join(condiciones) if condiciones else ""

    #traer registros paginados
    sql_datos = f"""
        SELECT id, nombre, email, activo
        FROM socios
        {where}
        ORDER BY id ASC
        LIMIT :limit OFFSET :offset;
    """
    params_datos = {**parametros, "limit": limit, "offset": offset}
    socios = ejecutar_consulta(sql_datos, params_datos) or []

    # formateo de booleanos
    socios = convertir_booleanos(socios, ["activo"])

    # total para paginar
    sql_total = f"""
        SELECT COUNT(*) AS total
        FROM socios
        {where};
    """
    res_total = ejecutar_consulta(sql_total, parametros)
    total = res_total[0]["total"] if res_total else 0

    return socios, total



    # el resto falta cambiar ----------------------------------



def insertar_socio(nombre: str, email: str, activo: bool) -> int:
    connection = conexion()
    cursor = obtener_cursor(connection)

    try:
        query = """
            INSERT INTO socios (nombre, email, activo)
            VALUES (%s, %s, %s);
        """
        cursor.execute(query, (nombre, email, activo))
        connection.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        connection.close()

def buscar_socio_por_id(id):
    connection = conexion()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT id, nombre, email, activo
            FROM socios
            WHERE id = %s;
            """,
            (id,)
        )

        socio = cursor.fetchone()

        if socio:
            socio["activo"] = bool(socio["activo"])

        return socio

    finally:
        cursor.close()
        connection.close()

def actualizar_socio_en_base(id: int, datos: dict) -> bool:
    
    connection = conexion()
    cursor = connection.cursor(dictionary=True)

    try:
        if 'nombre' in datos:
            cursor.execute(
                """
                UPDATE socios
                SET nombre = %s
                WHERE id = %s;
                """, 
                (datos['nombre'], id)
            )
        if 'email' in datos:
            cursor.execute(
                """
                UPDATE socios
                SET email = %s
                WHERE id = %s;
                """, 
                (datos['email'], id)
            )
        if 'activo' in datos:
            cursor.execute(
                """
                UPDATE socios
                SET activo = %s
                WHERE id = %s;
                """, 
                (datos['activo'], id)
            )

        connection.commit()

    finally:
        cursor.close()
        connection.close()

    return True