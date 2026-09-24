from src.repositories.db import conexion, obtener_cursor


def listar_socios(nombre: str, activo: bool, limit: int, offset: int):

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