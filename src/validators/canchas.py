from datetime import datetime
from src.constants import (
    ERROR_CODE_INVALID_BODY,
    ERROR_CODE_INVALID_PARAM,
    FORMATO_FECHA,
    HORA_APERTURA,
    HORA_CIERRE,
    DURACION_MINIMA_HORAS,
    DURACION_MAXIMA_HORAS,
)
from src.utils import (
    construir_error_api,
    validar_string_no_vacio,
    validar_positivo,
    validar_mayor_a_uno,
    validar_booleano,
)


# valida y parsea los parametros de consulta para filtrado de canchas (query params)
# por ejemplo: transforma 'techada=true' en un valor booleano True o lanza error 400 si es invalido
def validar_filtros_canchas(args):
    id_deporte = args.get('id_deporte', type=int)
    nombre = args.get('nombre', type=str)
    techada = args.get('techada', type=str)
    activa = args.get('activa', type=str)

    if techada is not None and techada.lower() not in ("true", "false"):
        raise ValueError(
            construir_error_api(
                code=ERROR_CODE_INVALID_PARAM,
                message="Parámetro inválido",
                description="techada debe ser true o false",
            )
        )

    if activa is not None and activa.lower() not in ("true", "false"):
        raise ValueError(
            construir_error_api(
                code=ERROR_CODE_INVALID_PARAM,
                message="Parámetro inválido",
                description="activa debe ser true o false",
            )
        )

    return {
        "id_deporte": id_deporte,
        "nombre": nombre,
        "techada": techada.lower() == "true" if techada is not None else None,
        "activa": activa.lower() == "true" if activa is not None else None,
    }


<<<<<<< HEAD

=======
# valida que los parametros de paginacion _limit y _offset sean enteros validos
# por example: _limit debe estar entre 1 y 100, y _offset no puede ser negativo
def validar_paginacion(args):
    try:
        limit = int(args.get('_limit', 10))
        offset = int(args.get('_offset', 0))
    except (ValueError, TypeError):
        raise ValueError(
            construir_error_api(
                code=ERROR_CODE_INVALID_PARAM,
                message="Parámetro inválido",
                description="_limit y _offset deben ser números enteros",
            )
        )

    if not (1 <= limit <= 100) or offset < 0:
        raise ValueError(
            construir_error_api(
                code=ERROR_CODE_INVALID_PARAM,
                message="Parámetro inválido",
                description="_limit debe estar entre 1 y 100, y _offset no puede ser negativo",
            )
        )

    return limit, offset
>>>>>>> reservas-marcos


# valida el cuerpo de la solicitud al crear una cancha (POST) acumulando todos los errores
# por ejemplo: asigna techada=False y activa=True por defecto si no vienen en el json
def validar_body_nueva_cancha(body: dict) -> dict:
    if not isinstance(body, dict):
        raise ValueError(
            construir_error_api(
                code=ERROR_CODE_INVALID_BODY,
                message='Cuerpo de la solicitud inválido',
                description='El cuerpo debe ser un JSON válido con Content-Type application/json',
            )
        )

    errores = []

    nombre = None
    id_deporte = None
    precio_hora = None
    techada = None
    activa = None

    try:
        nombre = validar_string_no_vacio(body.get('nombre'), 'nombre')
    except ValueError as e:
        errores.extend(e.args[0]["errors"])

    try:
        id_deporte = validar_positivo(body.get('id_deporte'), 'id_deporte')
    except ValueError as e:
        errores.extend(e.args[0]["errors"])

    try:
        precio_hora = validar_mayor_a_uno(body.get('precio_hora'), 'precio_hora')
    except ValueError as e:
        errores.extend(e.args[0]["errors"])

    try:
        techada = validar_booleano(body.get('techada'), 'techada', default=False)
    except ValueError as e:
        errores.extend(e.args[0]["errors"])

    try:
        activa = validar_booleano(body.get('activa'), 'activa', default=True)
    except ValueError as e:
        errores.extend(e.args[0]["errors"])

    if errores:
        raise ValueError({'errors': errores})

    return {
        "nombre": nombre,
        "id_deporte": id_deporte,
        "precio_hora": precio_hora,
        "techada": techada,
        "activa": activa,
    }


# valida el cuerpo para actualizaciones parciales de canchas (PATCH)
# por ejemplo: valida unicamente los campos presentes en el json recibido
def validar_body_modificar_cancha(body: dict) -> dict:
    if not isinstance(body, dict) or not body:
        raise ValueError(
            construir_error_api(
                code=ERROR_CODE_INVALID_BODY,
                message="Solicitud invalida",
                description="El cuerpo no puede estar vacío en una actualización",
            )
        )

    errores = []
    campos_actualizados = {}

    if "nombre" in body:
        try:
            campos_actualizados["nombre"] = validar_string_no_vacio(
                body.get("nombre"), "nombre"
            )
        except ValueError as e:
            errores.extend(e.args[0]["errors"])

    if "precio_hora" in body:
        try:
            campos_actualizados["precio_hora"] = validar_mayor_a_uno(
                body.get("precio_hora"), "precio_hora"
            )
        except ValueError as e:
            errores.extend(e.args[0]["errors"])

    if "techada" in body:
        try:
            campos_actualizados["techada"] = validar_booleano(
                body.get("techada"), "techada"
            )
        except ValueError as e:
            errores.extend(e.args[0]["errors"])

    if "activa" in body:
        try:
            campos_actualizados["activa"] = validar_booleano(
                body.get("activa"), "activa"
            )
        except ValueError as e:
            errores.extend(e.args[0]["errors"])

    if not campos_actualizados and not errores:
        raise ValueError(
            construir_error_api(
                code=ERROR_CODE_INVALID_BODY,
                message="Cuerpo de la solicitud inválido",
                description="Debe incluirse al menos un campo válido para actualizar",
            )
        )

    if errores:
        raise ValueError({'errors': errores})

    return campos_actualizados


# valida la consulta de disponibilidad de canchas (fecha, horarios en punto, rango comercial y momento futuro)
# por ejemplo: valida que la reserva sea en punto (e.g. 18:00 a 19:00) y posterior a la fecha/hora actual
def validar_disponibilidad(args):
    fecha_str = args.get('fecha', type=str)
    hora_inicio_str = args.get('hora_inicio', type=str)
    hora_fin_str = args.get('hora_fin', type=str)
    id_deporte = args.get('id_deporte', type=int)
    techada = args.get('techada', type=str)

    if not fecha_str or not hora_inicio_str or not hora_fin_str:
        raise ValueError(
            construir_error_api(
                code=ERROR_CODE_INVALID_PARAM,
                message="Parámetros obligatorios faltantes",
                description="fecha, hora_inicio y hora_fin son obligatorios",
            )
        )

    if techada is not None and techada.lower() not in ("true", "false"):
        raise ValueError(
            construir_error_api(
                code=ERROR_CODE_INVALID_PARAM,
                message="Parámetro inválido",
                description="techada debe ser true o false",
            )
        )

    try:
        fecha = datetime.strptime(fecha_str, FORMATO_FECHA).date()
    except ValueError:
        raise ValueError(
            construir_error_api(
                code=ERROR_CODE_INVALID_PARAM,
                message="Parámetro inválido",
                description=f"fecha debe tener el formato {FORMATO_FECHA}",
            )
        )

    try:
        hora_inicio = datetime.strptime(hora_inicio_str, "%H:%M")
        hora_fin = datetime.strptime(hora_fin_str, "%H:%M")
    except ValueError:
        raise ValueError(
            construir_error_api(
                code=ERROR_CODE_INVALID_PARAM,
                message="Parámetro inválido",
                description="hora_inicio y hora_fin deben tener el formato HH:MM",
            )
        )

    if hora_inicio.minute != 0 or hora_fin.minute != 0:
        raise ValueError(
            construir_error_api(
                code=ERROR_CODE_INVALID_PARAM,
                message="Parámetro inválido",
                description="Los horarios deben comenzar y terminar en horas en punto",
            )
        )

    inicio_dt = datetime.combine(fecha, hora_inicio.time())
    fin_dt = datetime.combine(fecha, hora_fin.time())

    if inicio_dt >= fin_dt:
        raise ValueError(
            construir_error_api(
                code=ERROR_CODE_INVALID_PARAM,
                message="Parámetro inválido",
                description="hora_inicio debe ser anterior a hora_fin",
            )
        )

    duracion_horas = (fin_dt - inicio_dt).total_seconds() / 3600
    if not (DURACION_MINIMA_HORAS <= duracion_horas <= DURACION_MAXIMA_HORAS):
        raise ValueError(
            construir_error_api(
                code=ERROR_CODE_INVALID_PARAM,
                message="Parámetro inválido",
                description=f"La duración debe ser entre {DURACION_MINIMA_HORAS} y {DURACION_MAXIMA_HORAS} horas",
            )
        )

    if hora_inicio.hour < HORA_APERTURA or hora_fin.hour > HORA_CIERRE:
        raise ValueError(
            construir_error_api(
                code=ERROR_CODE_INVALID_PARAM,
                message="Parámetro inválido",
                description=f"El horario debe estar entre las {HORA_APERTURA}:00 y las {HORA_CIERRE}:00",
            )
        )

    if inicio_dt <= datetime.now():
        raise ValueError(
            construir_error_api(
                code=ERROR_CODE_INVALID_PARAM,
                message="Parámetro inválido",
                description="El horario debe ser posterior al momento actual",
            )
        )

    return {
        "fecha": fecha_str,
        "hora_inicio": hora_inicio_str,
        "hora_fin": hora_fin_str,
        "id_deporte": id_deporte,
        "techada": techada.lower() == "true" if techada is not None else None,
    }