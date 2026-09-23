from src.repositories.socios import listar_socios
from src.repositories.socios import buscar_socio_por_id
from src.utils import validar_limit, validar_no_negativo, validar_booleano, validar_positivo, validar_string_no_vacio


def obtener_socios(nombre, activo, limit, offset):
    limit= validar_limit(limit, 'limit')
    offset = validar_no_negativo(offset, 'offset')
    activo = validar_booleano(activo, 'activo', default=None)

    return listar_socios(nombre, activo, limit, offset)

def crear_socio(datos: dict) -> dict:

    nombre = validar_string_no_vacio(datos.get('nombre'), 'nombre')
    email = validar_string_no_vacio(datos.get('email'), 'email')
    activo = True

def obtener_socio_por_id(id):
    
    return buscar_socio_por_id(id)