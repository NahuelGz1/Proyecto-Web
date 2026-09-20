from src.constants import ERROR_CODE_CANCHA_NOT_FOUND
from src.utils import construir_error_api
from src.repositories.canchas import contar_canchas, listar_canchas, obtener_cancha_por_id
from src.validators.canchas import validar_filtros_canchas, validar_paginacion
from src.repositories.canchas import existe_deporte, crear_cancha
from src.validators.canchas import validar_body_nueva_cancha
from src.utils import construir_error_api

def obtener_listado_canchas(args):
    filtros = validar_filtros_canchas(args)
    limit, offset = validar_paginacion(args)

    total = contar_canchas(filtros)
    canchas = listar_canchas(filtros, limit, offset)

    return canchas, total, limit, offset


def obtener_cancha(cancha_id):
    cancha = obtener_cancha_por_id(cancha_id)

    if not cancha:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_CANCHA_NOT_FOUND,
            message='Cancha no encontrada',
            description=f"No existe una cancha con id '{cancha_id}'"
        ), 404)

    return cancha


def registrar_cancha(body: dict) -> dict:
    datos_validados = validar_body_nueva_cancha(body)

    if not existe_deporte(datos_validados["id_deporte"]):
        raise ValueError(construir_error_api(
            code='deporte.not.found',
            message='Deporte no encontrado',
            description=f"No existe un deporte con id '{datos_validados['id_deporte']}'"
        ), 404)

    nuevo_id = crear_cancha(
        nombre=datos_validados["nombre"],
        id_deporte=datos_validados["id_deporte"],
        precio_hora=datos_validados["precio_hora"],
        techada=datos_validados["techada"],
        activa=datos_validados["activa"],
    )
    return obtener_cancha(nuevo_id)


def actualizar_cancha(cancha_id: int, body: dict) -> None:
    pass

def borrar_cancha(cancha_id: int) -> None:
    pass


def obtener_canchas_disponibles(args: dict) -> tuple[list[dict], int, int, int]:
    pass