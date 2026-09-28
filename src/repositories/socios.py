from src.repositories.db import ejecutar_consulta, ejecutar_mutacion
from src.utils import convertir_booleanos


# funcion auxiliar para construir la clausula WHERE dinamicamente segun los filtros
# por ejemplo: si le pasas {"nombre": "Juan", "activo": True}, te genera 'WHERE nombre LIKE :nombre AND activo = :activo'
def _armar_where(filtros: dict):
    condiciones = []
    parametros = {}

    if filtros.get("nombre"):
        condiciones.append("nombre LIKE :nombre")
        parametros["nombre"] = f"%{filtros['nombre']}%"

    if filtros.get("activo") is not None:
        condiciones.append("activo = :activo")
        parametros["activo"] = filtros["activo"]

    where_sql = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""
    return where_sql, parametros


# cuenta la cantidad total de socios que coinciden con los filtros para calcular la paginacion
# por ejemplo: devuelve 42 si hay 42 socios activos en total
def contar_socios(filtros: dict) -> int:
    where_sql, params = _armar_where(filtros)
    sql = f"SELECT COUNT(*) AS total FROM socios {where_sql};"
    filas = ejecutar_consulta(sql, params)
    return filas[0]["total"] if filas else 0


# trae la lista de socios paginada y filtrada convirtiendo los 0 y 1 a booleanos
# por ejemplo: listar_socios({"activo": True}, limit=10, offset=0) trae los primeros 10 activos
def listar_socios(filtros: dict, limit: int, offset: int) -> list[dict]:
    where_sql, params = _armar_where(filtros)
    params["limit"] = limit
    params["offset"] = offset

    sql = f"""
        SELECT id, nombre, email, activo
        FROM socios
        {where_sql}
        ORDER BY id ASC
        LIMIT :limit OFFSET :offset;
    """
    return convertir_booleanos(ejecutar_consulta(sql, params))


# busca los datos de un unico socio por su id
# por ejemplo: buscar_socio_por_id(5) devuelve {"id": 5, "nombre": "Ana", ...} o None si no existe
def buscar_socio_por_id(id_socio: int) -> dict | None:
    sql = """
          SELECT id, nombre, email, activo
          FROM socios
          WHERE id = :id_socio; \
          """
    filas = ejecutar_consulta(sql, {"id_socio": id_socio})
    if filas:
        return convertir_booleanos(filas)[0]
    return None


# inserta un nuevo socio en la tabla socios y retorna el id asignado por la base de datos
# por ejemplo: insertar_socio("Carlos", "carlos@gmail.com", True) devuelve 15
def insertar_socio(nombre: str, email: str, activo: bool) -> int:
    sql = """
          INSERT INTO socios (nombre, email, activo)
          VALUES (:nombre, :email, :activo); \
          """
    return ejecutar_mutacion(
        sql,
        {
            "nombre": nombre,
            "email": email,
            "activo": activo,
        },
    )


# actualiza unicamente los campos recibidos en el diccionario 'datos'
# por ejemplo: si le pasas {"activo": False}, genera 'UPDATE socios SET activo = :activo WHERE id = :id_socio'
def actualizar_socio_en_base(id_socio: int, datos: dict) -> None:
    if not datos:
        return

    set_clauses = [f"{campo} = :{campo}" for campo in datos.keys()]
    set_sql = ", ".join(set_clauses)

    sql = f"""
        UPDATE socios
        SET {set_sql}
        WHERE id = :id_socio;
    """

    parametros = dict(datos)
    parametros["id_socio"] = id_socio

    ejecutar_mutacion(sql, parametros)