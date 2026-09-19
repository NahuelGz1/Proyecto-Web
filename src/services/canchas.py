from src.repositories.canchas import contar_canchas, listar_canchas, obtener_cancha_por_id
from src.validators.canchas import validar_filtros_canchas, validar_paginacion
from src.repositories.canchas import existe_deporte, crear_cancha
from src.validators.canchas import validar_cancha_create


def obtener_listado_canchas(args):
    filtros = validar_filtros_canchas(args)
    limit, offset = validar_paginacion(args)

    total = contar_canchas(filtros)
    canchas = listar_canchas(filtros, limit, offset)

    return canchas, total, limit, offset


def obtener_cancha(cancha_id):
    return obtener_cancha_por_id(cancha_id)


def crear_cancha_service(data):
    datos_validados = validar_cancha_create(data)

    if not existe_deporte(datos_validados["id_deporte"]):
        raise ValueError("El deporte indicado no existe")

    nuevo_id = crear_cancha(datos_validados)
    return obtener_cancha(nuevo_id)