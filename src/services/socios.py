from src.repositories.socios import listar_socios

def obtener_socios(nombre,activo,limit,offset):
    return listar_socios(nombre,activo,limit,offset)
