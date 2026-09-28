from datetime import datetime, timedelta

from src.constants import (
    DURACION_MAXIMA_HORAS,
    DURACION_MINIMA_HORAS,
    ERROR_CODE_CANCHA_NOT_FOUND,
    ERROR_CODE_HORARIO_OCUPADO,
    ERROR_CODE_INVALID_BODY,
    ERROR_CODE_INVALID_PARAM,
    ERROR_CODE_RESERVA_NOT_FOUND,
    ERROR_CODE_SOCIO_NOT_FOUND,
    ERROR_CODE_TRANSICION_INVALIDA,
    ESTADO_CANCELADA,
    ESTADO_CONFIRMADA,
    ESTADO_FINALIZADA,
    HORA_APERTURA,
    HORA_CIERRE,
)

from src.repositories.canchas import obtener_cancha_por_id
from src.repositories.reservas import (
    actualizar_reserva,
    contar_reservas,
    crear_reserva,
    existe_superposicion,
    listar_reservas,
    obtener_reserva_por_id,
)
from src.repositories.socios import buscar_socio_por_id

from src.utils import (
    construir_error_api,
    validar_id,
    validar_mayor_a_uno,
    validar_paginacion,
)

from src.validators.canchas import validar_filtros_canchas
from src.validators.reservas import (
    validar_crear_reserva,
    validar_datos_actualizar_reserva,
    validar_filtros_reservas,
)


def obtener_listado_reservas(args: dict):
    filtros = validar_filtros_reservas(args)
    limit, offset = validar_paginacion(args)
    total = contar_reservas(filtros)

    if total == 0:
        return None # señal para que la ruta devuelva un 204 sin contenido

    reservas = listar_reservas(filtros, limit, offset) # consulta a la base de datos

    return reservas, total, limit, offset


def obtener_reserva(id_reserva):
    """Obtiene una reserva por ID y formatea sus fechas"""
    id_reserva = validar_id(id_reserva)

    reserva = obtener_reserva_por_id(id_reserva)
    if not reserva:
        raise ValueError(
            construir_error_api(
                code=ERROR_CODE_RESERVA_NOT_FOUND,
                message="Recurso no encontrado",
                description=f"No se encontró la reserva con id {id_reserva}",
            ),
            404,
        )

    # convierte las fechas al formato ISO del Swagger
    if "fecha_hora_inicio" in reserva and reserva["fecha_hora_inicio"]:
        reserva["fecha_hora_inicio"] = reserva["fecha_hora_inicio"].isoformat()
    if "fecha_hora_fin" in reserva and reserva["fecha_hora_fin"]:
        reserva["fecha_hora_fin"] = reserva["fecha_hora_fin"].isoformat()

    return reserva


def crear_nueva_reserva(datos):
    """Valida los datos y crea la reserva si todo es correcto"""
    datos_validados = validar_crear_reserva(datos)

    id_socio = datos_validados.get("id_socio")
    id_cancha = datos_validados.get("id_cancha")
    fecha_inicio = datos_validados.get("fecha_hora_inicio")
    fecha_fin = datos_validados.get("fecha_hora_fin")

    # validar que el socio exista en la base
    socio = buscar_socio_por_id(id_socio)
    if not socio:
        raise ValueError(
            construir_error_api(
                code=ERROR_CODE_SOCIO_NOT_FOUND,
                message="Recurso no encontrado",
                description=f"No se encontró el socio con id {id_socio}",
            ),
            404,
        )

    # validar que la cancha exista en la BD
    cancha = obtener_cancha_por_id(id_cancha)
    if not cancha:
        raise ValueError(
            construir_error_api(
                code=ERROR_CODE_CANCHA_NOT_FOUND,
                message="Recurso no encontrado",
                description=f"No se encontró la cancha con id {id_cancha}",
            ),
            404,
        )

    # validar superposición de horarios
    if existe_superposicion(id_cancha, fecha_inicio, fecha_fin):
        raise ValueError(
            construir_error_api(
                code=ERROR_CODE_HORARIO_OCUPADO,
                message="Horario no disponible",
                description="La cancha ya se encuentra reservada en el rango horario solicitado",
            ),
            409,
        )

    # crear la reserva en la base
    nuevo_id = crear_reserva(
        id_cancha=id_cancha,
        id_socio=id_socio,
        fecha_hora_inicio=fecha_inicio,
        fecha_hora_fin=fecha_fin,
        precio_hora=datos_validados.get("precio_hora"),
        precio_total=datos_validados.get("precio_total"),
        estado=ESTADO_CONFIRMADA,
    )

    #retorna la reserva creada
    return obtener_reserva(nuevo_id)





def modificar_reserva(id_reserva, body: dict):

    id_reserva = validar_id(id_reserva)
    # 1. Validar formato de los datos que vienen en el body (lanza 400 si falla)
    datos_validados = validar_datos_actualizar_reserva(body)

    # 2. Verificar que la reserva exista en la base de datos (404)
    reserva_existente = obtener_reserva_por_id(id_reserva)
    if not reserva_existente:
        payload = construir_error_api(
            code="NOT_FOUND",
            message="Reserva no encontrada",
            description=f"No se encontró ninguna reserva con el id {id_reserva}",
        )
        # Lanzamos ValueError con código 404; procesar_error_api lo respetará
        raise ValueError(payload, 404)

    # 3. Ejecutar actualización
    actualizar_reserva(id_reserva, datos_validados)

    # 4. Devolver la entidad actualizada
    return obtener_reserva(id_reserva)
