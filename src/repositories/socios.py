from src.repositories.db import conexion


def listar_socios(nombre, activo, limit, offset):

    connection = conexion()
    cursor = connection.cursor(dictionary=True)

    try:
        condiciones = []
        parametros = []

        if nombre:
            condiciones.append("nombre LIKE %s")
            parametros.append(f"%{nombre}%")

        if activo is not None:
            condiciones.append("activo = %s")
            parametros.append(activo)

        where = ""

        if condiciones:
            where = "WHERE " + " AND ".join(condiciones)

        cursor.execute(
            f"""
            SELECT id, nombre, email, activo
            FROM socios
            {where}
            ORDER BY id ASC
            LIMIT %s OFFSET %s;
            """,
            parametros + [limit, offset]
        )

        socios = cursor.fetchall()

        for socio in socios:
            socio["activo"] = bool(socio["activo"])
            
        cursor.execute(
            f"""
            SELECT COUNT(*) AS total
            FROM socios
            {where};
            """,
            parametros
        )

        total = cursor.fetchone()["total"]

        return socios, total

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