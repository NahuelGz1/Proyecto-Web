from datetime import datetime, timezone

from src.constants import (
    ERROR_CODE_CANCHA_NOT_FOUND,
    ERROR_CODE_HORARIO_OCUPADO,
    ERROR_CODE_RESERVA_NOT_FOUND,
    ERROR_CODE_SOCIO_NOT_FOUND,
    ERROR_CODE_TRANSICION_INVALIDA,
    ESTADO_CANCELADA,
    ESTADO_CONFIRMADA,
    ESTADO_FINALIZADA,
)
from src.repositories import reservas as reservas_repository
from src.utils import construir_error_api


def listar_reservas(filtros: dict, limit: int, offset: int):
    return reservas_repository.obtener_todas(
        filtros=filtros, limit=limit, offset=offset
    )


def obtener_listado_reservas(filtros: dict, limit: int, offset: int):
    return listar_reservas(filtros, limit, offset)


def obtener_reserva_por_id(id_reserva: int):
    reserva = reservas_repository.obtener_por_id(id_reserva)
    if not reserva:
        raise ValueError(
            construir_error_api(
                code=ERROR_CODE_RESERVA_NOT_FOUND,
                message="Reserva no encontrada",
                level="error",
                description=f"No se encontró ninguna reserva con el ID {id_reserva}",
            ),
            404,
        )
    return reserva


def obtener_reserva(id_reserva: int):
    return obtener_reserva_por_id(id_reserva)


def crear_reserva(datos: dict):
    #validar que la fecha de inicio no sea pasada
    try:
        fecha_inicio_raw = datos.get("fecha_hora_inicio", "")
        if isinstance(fecha_inicio_raw, str):
            fecha_inicio = datetime.fromisoformat(fecha_inicio_raw.replace("Z", "+00:00"))
        else:
            fecha_inicio = fecha_inicio_raw

        ahora = datetime.now(fecha_inicio.tzinfo or timezone.utc)
        if fecha_inicio < ahora:
            raise ValueError(
                construir_error_api(
                    code="bad_request.fecha_pasada",
                    message="Fecha inválida",
                    level="error",
                    description="No se pueden realizar reservas en fechas u horas pasadas",
                ),
                400,
            )
    except (ValueError, TypeError) as e:
        if isinstance(e, ValueError) and len(e.args) > 1 and isinstance(e.args[1], int):
            raise e
        raise ValueError(
            construir_error_api(
                code="bad_request.formato_fecha",
                message="Formato de fecha inválido",
                level="error",
                description="El formato de la fecha de inicio es incorrecto",
            ),
            400,
        )

    #verificar existencia y estado del socio
    socio = reservas_repository.obtener_estado_socio(datos["id_socio"])
    if not socio:
        raise ValueError(
            construir_error_api(
                code=ERROR_CODE_SOCIO_NOT_FOUND,
                message="Socio no encontrado",
                level="error",
                description=f"El socio con ID {datos['id_socio']} no existe en el sistema",
            ),
            404,
        )

    if not socio.get("activo", True):
        raise ValueError(
            construir_error_api(
                code="conflict.socio_inactivo",
                message="Socio inactivo",
                level="error",
                description=f"El socio con ID {datos['id_socio']} se encuentra inactivo",
            ),
            409,
        )

    #verificar existencia y estado de la cancha
    cancha = reservas_repository.obtener_estado_cancha(datos["id_cancha"])
    if not cancha:
        raise ValueError(
            construir_error_api(
                code=ERROR_CODE_CANCHA_NOT_FOUND,
                message="Cancha no encontrada",
                level="error",
                description=f"La cancha con ID {datos['id_cancha']} no existe en el sistema",
            ),
            404,
        )

    if not cancha.get("activa", True):
        raise ValueError(
            construir_error_api(
                code="conflict.cancha_inactiva",
                message="Cancha inactiva",
                level="error",
                description=f"La cancha con ID {datos['id_cancha']} se encuentra inactiva",
            ),
            409,
        )

    # validar superposición de horarios
    hay_solapamiento = reservas_repository.verificar_solapamiento(
        id_cancha=datos["id_cancha"],
        fecha_hora_inicio=datos["fecha_hora_inicio"],
        fecha_hora_fin=datos["fecha_hora_fin"],
    )
    if hay_solapamiento:
        raise ValueError(
            construir_error_api(
                code=ERROR_CODE_HORARIO_OCUPADO,
                message="Horario no disponible",
                level="error",
                description="La cancha ya se encuentra reservada en el rango horario solicitado",
            ),
            409,
        )

    datos["estado"] = ESTADO_CONFIRMADA
    return reservas_repository.crear(datos)


def crear_nueva_reserva(datos: dict):
    return crear_reserva(datos)


def actualizar_reserva(id_reserva: int, datos: dict):
    reserva_actual = obtener_reserva_por_id(id_reserva)

    id_cancha = datos.get("id_cancha", reserva_actual["id_cancha"])
    inicio = datos.get("fecha_hora_inicio", reserva_actual["fecha_hora_inicio"])
    fin = datos.get("fecha_hora_fin", reserva_actual["fecha_hora_fin"])

    if "id_cancha" in datos and not reservas_repository.existe_cancha(id_cancha):
        raise ValueError(
            construir_error_api(
                code=ERROR_CODE_CANCHA_NOT_FOUND,
                message="Cancha no encontrada",
                level="error",
                description=f"La cancha con ID {id_cancha} no existe en el sistema",
            ),
            404,
        )

    hay_solapamiento = reservas_repository.verificar_solapamiento(
        id_cancha=id_cancha,
        fecha_hora_inicio=inicio,
        fecha_hora_fin=fin,
        id_reserva_excluir=id_reserva,
    )
    if hay_solapamiento:
        raise ValueError(
            construir_error_api(
                code=ERROR_CODE_HORARIO_OCUPADO,
                message="Horario no disponible",
                level="error",
                description="La cancha ya se encuentra reservada en el nuevo rango horario",
            ),
            409,
        )

    return reservas_repository.actualizar(id_reserva, datos)


def cambiar_estado_reserva(id_reserva: int, nuevo_estado: str):
    #buscar la reserva actual
    reserva_actual = obtener_reserva_por_id(id_reserva)
    estado_actual = reserva_actual["estado"]

    if estado_actual == nuevo_estado:
        return reserva_actual

    #si ya está cancelada o finalizada y se intenta cambiar a OTRO estado, lanza error 400
    if estado_actual in (ESTADO_CANCELADA, ESTADO_FINALIZADA):
        raise ValueError(
            construir_error_api(
                code=ERROR_CODE_TRANSICION_INVALIDA,
                message="Transición de estado inválida",
                level="error",
                description=f"No se puede cambiar el estado de una reserva que está '{estado_actual}'",
            ),
            400,
        )

    #si la transición es válida, actualiza en la BD
    return reservas_repository.actualizar_estado(id_reserva, nuevo_estado)