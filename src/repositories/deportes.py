from src.repositories.db import ejecutar_consulta


# trae la lista completa de deportes ordenados por su id de forma ascendente
# por ejemplo: devuelve [{"id": 1, "nombre": "Fútbol"}, {"id": 2, "nombre": "Tenis"}]
def listar_deportes() -> list[dict]:
    sql = "SELECT id, nombre FROM deportes ORDER BY id ASC;"
    return ejecutar_consulta(sql)