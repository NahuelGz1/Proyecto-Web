from src.repositories.db import ejecutar_consulta


def listar_deportes() -> list[dict]:
    sql = "SELECT id, nombre FROM deportes ORDER BY id ASC;"
    return ejecutar_consulta(sql)