from src.constants import ERROR_CODE_CANCHA_NOT_FOUND
from src.utils import construir_error_api

from src.repositories.canchas import (
    contar_canchas,
    listar_canchas,
    obtener_cancha_por_id,
    existe_deporte,
    crear_cancha,
    modificar_cancha,
    eliminar_cancha,
    tiene_reservas_asociadas,
    contar_canchas_disponibles,
    listar_canchas_disponibles,
)

from src.validators.canchas import (
    validar_filtros_canchas,
    validar_paginacion,
    validar_body_nueva_cancha,
    validar_body_modificar_cancha,
    validar_disponibilidad,
)

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

# 23/9 ----------------------------------------------------------------------------------- (PATCH)
# valida body que le llega y manda cambios a modificar_cancha
def actualizar_cancha(cancha_id: int, body: dict) -> None:
    campos_validados = validar_body_modificar_cancha(body)

    obtener_cancha(cancha_id)

    modificar_cancha(cancha_id, campos_validados)

def borrar_cancha(cancha_id: int) -> None:
    obtener_cancha(cancha_id)

    if tiene_reservas_asociadas(cancha_id):
        raise ValueError(
            construir_error_api(
                code="cancha.has.reservations",
                message="Conflicto de integridad",
                description=f"No se puede eliminar la cancha con id '{cancha_id}' porque tiene reservas asociadas",
            ),
            409,
        )

    # 3. Elimina la cancha
    eliminar_cancha(cancha_id)


def obtener_canchas_disponibles(args):

    datos = validar_disponibilidad(args)
    limit, offset = validar_paginacion(args)

    filtros = {"id_deporte": datos["id_deporte"], "techada": datos["techada"]}

    total = contar_canchas_disponibles(datos["fecha"], datos["hora_inicio"], datos["hora_fin"], filtros)
    canchas = listar_canchas_disponibles(datos["fecha"], datos["hora_inicio"], datos["hora_fin"], filtros, limit, offset)

    return canchas, total, limit, offset