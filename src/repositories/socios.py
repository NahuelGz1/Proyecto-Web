from src.repositories.db import ejecutar_consulta, ejecutar_mutacion


def listar_socios(nombre: str, activo: bool, limit: int, offset: int):
    condiciones = []
    parametros = {}

    if nombre:
        condiciones.append("nombre LIKE :nombre")
        parametros["nombre"] = f"%{nombre}%"

    if activo is not None:
        condiciones.append("activo = :activo")
        parametros["activo"] = activo

    where = ""
    if condiciones:
        where = "WHERE " + " AND ".join(condiciones)

    sql_socios = f"""
        SELECT id, nombre, email, activo
        FROM socios
        {where}
        ORDER BY id ASC
        LIMIT :limit OFFSET :offset;
    """
    params_socios = dict(parametros)
    params_socios["limit"] = limit
    params_socios["offset"] = offset

    socios = ejecutar_consulta(sql_socios, params_socios)

    for socio in socios:
        socio["activo"] = bool(socio["activo"])

    sql_total = f"""
        SELECT COUNT(*) AS total
        FROM socios
        {where};
    """
    resultado_total = ejecutar_consulta(sql_total, parametros)
    total = resultado_total[0]["total"] if resultado_total else 0

    return socios, total


def insertar_socio(nombre: str, email: str, activo: bool) -> int:
    query = """
        INSERT INTO socios (nombre, email, activo)
        VALUES (:nombre, :email, :activo);
    """
    parametros = {
        "nombre": nombre,
        "email": email,
        "activo": activo
    }
    return ejecutar_mutacion(query, parametros)


def buscar_socio_por_id(id):
    query = """
        SELECT id, nombre, email, activo
        FROM socios
        WHERE id = :id;
    """
    socios = ejecutar_consulta(query, {"id": id})

    if not socios:
        return None

    socio = socios[0]
    socio["activo"] = bool(socio["activo"])

    return socio


def actualizar_socio_en_base(id: int, datos: dict) -> bool:
    if 'nombre' in datos:
        ejecutar_mutacion(
            """
            UPDATE socios
            SET nombre = :nombre
            WHERE id = :id;
            """,
            {'nombre': datos['nombre'], 'id': id}
        )

    if 'email' in datos:
        ejecutar_mutacion(
            """
            UPDATE socios
            SET email = :email
            WHERE id = :id;
            """,
            {'email': datos['email'], 'id': id}
        )

    if 'activo' in datos:
        ejecutar_mutacion(
            """
            UPDATE socios
            SET activo = :activo
            WHERE id = :id;
            """,
            {'activo': datos['activo'], 'id': id}
        )

    return True