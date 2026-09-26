from src.constants import ERROR_CODE_CANCHA_NOT_FOUND
from src.utils import construir_error_api, validar_paginacion

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
    validar_body_nueva_cancha,
    validar_body_modificar_cancha,
    validar_disponibilidad,
)


# coordina la obtencion de canchas aplicando filtros y paginacion
# por ejemplo: recibe args={"techada": "true", "_limit": "10"} y retorna (lista_canchas, total, limit, offset)
def obtener_listado_canchas(args):
    filtros = validar_filtros_canchas(args)
    limit, offset = validar_paginacion(args)

    total = contar_canchas(filtros)
    canchas = listar_canchas(filtros, limit, offset)

    return canchas, total, limit, offset


# busca una cancha por su id y lanza error 404 si no existe
# por ejemplo: obtener_cancha(5) devuelve la cancha o lanza ValueError con status 404
def obtener_cancha(cancha_id):
    cancha = obtener_cancha_por_id(cancha_id)

    if not cancha:
        raise ValueError(
            construir_error_api(
                code=ERROR_CODE_CANCHA_NOT_FOUND,
                message='Cancha no encontrada',
                description=f"No existe una cancha con id '{cancha_id}'"
            ),
            404
        )

    return cancha


# procesa la creacion de una nueva cancha previa validaciones de campos y existencia del deporte
# por ejemplo: registrar_cancha({"nombre": "Cancha 1", "id_deporte": 2, ...}) retorna la cancha creada
def registrar_cancha(body: dict) -> dict:
    datos_validados = validar_body_nueva_cancha(body)

    if not existe_deporte(datos_validados["id_deporte"]):
        raise ValueError(
            construir_error_api(
                code='deporte.not.found',
                message='Deporte no encontrado',
                description=f"No existe un deporte con id '{datos_validados['id_deporte']}'"
            ),
            404
        )

    nuevo_id = crear_cancha(
        nombre=datos_validados["nombre"],
        id_deporte=datos_validados["id_deporte"],
        precio_hora=datos_validados["precio_hora"],
        techada=datos_validados["techada"],
        activa=datos_validados["activa"],
    )
    return obtener_cancha(nuevo_id)


# aplica cambios parciales sobre una cancha existente (PATCH)
# por example: actualizar_cancha(3, {"precio_hora": 2500}) modifica solo el precio si la cancha existe
def actualizar_cancha(cancha_id: int, body: dict) -> None:
    campos_validados = validar_body_modificar_cancha(body)

    obtener_cancha(cancha_id)

    modificar_cancha(cancha_id, campos_validados)


# elimina una cancha asegurando primero que exista y que no posea reservas vinculadas
# por ejemplo: si la cancha id=1 tiene reservas asociadas, lanza conflicto 409
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

    eliminar_cancha(cancha_id)


# busca y pagina las canchas libres para la fecha y rango horario especificados
# por ejemplo: recibe args con fecha, hora_inicio y hora_fin, devolviendo solo las que no estan reservadas
def obtener_canchas_disponibles(args):
    datos = validar_disponibilidad(args)
    limit, offset = validar_paginacion(args)

    filtros = {
        "id_deporte": datos["id_deporte"],
        "techada": datos["techada"]
    }

    total = contar_canchas_disponibles(
        datos["fecha"], datos["hora_inicio"], datos["hora_fin"], filtros
    )
    canchas = listar_canchas_disponibles(
        datos["fecha"], datos["hora_inicio"], datos["hora_fin"], filtros, limit, offset
    )

    return canchas, total, limit, offset