from src.repositories.db import ejecutar_consulta


def listar_socios(nombre, activo, limit, offset):
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

    # 1. Consulta para obtener los socios paginados
    params_socios = dict(parametros)
    params_socios["limit"] = limit
    params_socios["offset"] = offset

    sql_socios = f"""
        SELECT id, nombre, email, activo
        FROM socios
        {where}
        ORDER BY id ASC
        LIMIT :limit OFFSET :offset;
    """
    socios = ejecutar_consulta(sql_socios, params_socios)

    # Conversión explícita a booleano de la clave 'activo'
    for socio in socios:
        socio["activo"] = bool(socio["activo"])

    # 2. Consulta para obtener el total de registros con el filtro aplicado
    sql_total = f"""
        SELECT COUNT(*) AS total
        FROM socios
        {where};
    """
    resultado_total = ejecutar_consulta(sql_total, parametros)
    total = resultado_total[0]["total"] if resultado_total else 0

    return socios, total