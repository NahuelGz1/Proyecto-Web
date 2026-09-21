from src.repositories.socios import listar_socios
from utils import validar_limit, validar_no_negativo, validar_booleano, validar_positivo, validar_no_vacio


def obtener_socios(nombre, activo, limit, offset):
    limit= validar_limit(limit, 'limit')
    offset = validar_no_negativo(offset, 'offset')
    activo = validar_booleano(activo, 'activo', default=None)

    return listar_socios(nombre, activo, limit, offset)

def crear_socio(datos: dict) -> dict:

    nombre = validar_no_vacio(datos.get('nombre'), 'nombre')
    email = validar_no_vacio(datos.get('email'), 'email')
    activo = True



