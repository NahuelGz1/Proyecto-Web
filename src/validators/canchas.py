from src.constants import ERROR_CODE_INVALID_BODY, ERROR_CODE_INVALID_PARAM
from src.utils import (
    construir_error_api,
    validar_string_no_vacio,
    validar_positivo,
    validar_mayor_a_uno,
    validar_booleano,

)


def validar_filtros_canchas(args):
    id_deporte = args.get('id_deporte', type=int)
    nombre = args.get('nombre', type=str)
    techada = args.get('techada', type=str)
    activa = args.get('activa', type=str)

    if techada is not None and techada.lower() not in ("true", "false"):
        raise ValueError(construir_error_api(
            code=ERROR_CODE_INVALID_PARAM,
            message="Parámetro inválido",
            description="techada debe ser true o false"
        ))

    if activa is not None and activa.lower() not in ("true", "false"):
        raise ValueError(construir_error_api(
            code=ERROR_CODE_INVALID_PARAM,
            message="Parámetro inválido",
            description="activa debe ser true o false"
        ))

    return {
        "id_deporte": id_deporte,
        "nombre": nombre,
        "techada": techada.lower() == "true" if techada is not None else None,
        "activa": activa.lower() == "true" if activa is not None else None,
    }


def validar_paginacion(args):
    try:
        limit = int(args.get('_limit', 10))
        offset = int(args.get('_offset', 0))
    except ValueError:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_INVALID_PARAM,
            message="Parámetro inválido",
            description="_limit y _offset deben ser números enteros"
        ))

    if not (1 <= limit <= 100) or offset < 0:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_INVALID_PARAM,
            message="Parámetro inválido",
            description="_limit debe estar entre 1 y 100, y _offset no puede ser negativo"
        ))

    return limit, offset


def validar_body_nueva_cancha(body: dict) -> dict:
    """
    Valida el body del POST.
    Acepta nombre (nombre de cancha), id_deporte, precio_hora, techada, activa.
    """
    if body is None:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_INVALID_BODY,
            message='Cuerpo de la solicitud inválido',
            description='El cuerpo debe ser un JSON válido con Content-Type application/json'
        ))

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

##### CHEQUEAR ESTA LINEA BLOQUE LISANDRO ######

    if errores:
        raise ValueError({'errors': errores})

    return {
        "nombre": nombre,
        "id_deporte": id_deporte,
        "precio_hora": precio_hora,
        "techada": techada,
        "activa": activa,
    }


def validar_body_modificar_cancha(body: dict) -> dict:
    if not body:
        raise ValueError(construir_error_api(

        code=ERROR_CODE_INVALID_BODY,
        message="Solicitud invalida"
        description="no puede quedar vacio en una actualización"
        
        ))
    
        errores = []
        campos_actualizados = {}