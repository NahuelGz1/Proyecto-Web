from src.repositories.deportes import listar_deportes

def obtener_deportes():
    """
    Se encarga de coordinar la obtención de la lista de deportes disponibles.

    Precondiciones:
        - Ninguna.
    Postcondiciones:
        - Retorna una lista de diccionarios/tuplas con la información de cada deporte.
    """
    # Al no necesitar validaciones ni transformaciones de datos, la función le deja la consulta directamente al repositorio.
    return listar_deportes()
