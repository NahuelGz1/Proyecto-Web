
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
    contar_reservas,
    crear_reserva,
    existe_superposicion,
    listar_reservas,
    modificar_reserva,
    obtener_reserva_por_id,
)
from src.repositories.socios import buscar_socio_por_id
from src.utils import construir_error_api, validar_paginacion
from src.validators.canchas import validar_filtros_canchas
from src.validators.reservas import validar_filtros_reservas


def obtener_listado_reservas(args:dict):

    filtros = validar_filtros_reservas(args)
    limit, offset = validar_paginacion(args)
    total=contar_reservas(filtros)

    if total == 0:
        return None #señal para que la ruta devuelva un 204 sin contenido

    reservas = listar_reservas(filtros, limit, offset) #consulta a la base de datos

    return reservas, total, limit, offset
