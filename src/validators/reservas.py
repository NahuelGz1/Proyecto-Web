import re
from datetime import datetime

from src.constants import (
    ERROR_CODE_INVALID_BODY,
    ERROR_CODE_INVALID_FECHA,
    ERROR_CODE_INVALID_PARAM,
    ESTADO_CANCELADA,
    ESTADO_CONFIRMADA,
    ESTADO_FINALIZADA,
    FORMATO_FECHA,
)
from src.utils import (
    construir_error_api,
    validar_id,
    validar_string_no_vacio,
)

#expresión regular ajustada al contrato Swagger para ISO 8601 GMT-3
ISO_GMT3_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}-03:00$")

ESTADOS_PERMITIDOS = (
    ESTADO_CONFIRMADA,
    ESTADO_CANCELADA,
    ESTADO_FINALIZADA,
)


def validar_filtros_reservas(args: dict) -> dict:
    filtros = {}
    errores = []

    # Se usa .get() validando que la clave exista explícitamente
    if "id_cancha" in args and args.get("id_cancha") is not None:
        try:
            filtros["id_cancha"] = validar_id(args["id_cancha"])
        except ValueError:
            errores.append(
                {
                    "code": ERROR_CODE_INVALID_PARAM,
                    "message": "Parámetro inválido",
                    "level": "error",
                    "description": "El parámetro 'id_cancha' debe ser un número entero positivo mayor a 0",
                }
            )

    if "id_socio" in args and args.get("id_socio") is not None:
        try:
            filtros["id_socio"] = validar_id(args["id_socio"])
        except ValueError:
            errores.append(
                {
                    "code": ERROR_CODE_INVALID_PARAM,
                    "message": "Parámetro inválido",
                    "level": "error",
                    "description": "El parámetro 'id_socio' debe ser un número entero positivo mayor a 0",
                }
            )

    estado = args.get("estado")
    if estado:
        estado_limpio = str(estado).strip().lower()
        if estado_limpio not in ESTADOS_PERMITIDOS:
            errores.append(
                {
                    "code": ERROR_CODE_INVALID_PARAM,
                    "message": "Parámetro inválido",
                    "level": "error",
                    "description": f"El parámetro 'estado' debe ser uno de los siguientes valores: {', '.join(ESTADOS_PERMITIDOS)}",
                }
            )
        else:
            filtros["estado"] = estado_limpio

    fecha_desde = args.get("fecha_desde")
    if fecha_desde:
        try:
            datetime.strptime(str(fecha_desde).strip(), FORMATO_FECHA)
            filtros["fecha_desde"] = str(fecha_desde).strip()
        except ValueError:
            errores.append(
                {
                    "code": ERROR_CODE_INVALID_PARAM,
                    "message": "Parámetro inválido",
                    "level": "error",
                    "description": f"El parámetro 'fecha_desde' debe tener el formato 'YYYY-MM-DD'",
                }
            )

    fecha_hasta = args.get("fecha_hasta")
    if fecha_hasta:
        try:
            datetime.strptime(str(fecha_hasta).strip(), FORMATO_FECHA)
            filtros["fecha_hasta"] = str(fecha_hasta).strip()
        except ValueError:
            errores.append(
                {
                    "code": ERROR_CODE_INVALID_PARAM,
                    "message": "Parámetro inválido",
                    "level": "error",
                    "description": f"El parámetro 'fecha_hasta' debe tener el formato 'YYYY-MM-DD'",
                }
            )

    if errores:
        raise ValueError(construir_error_api(errores_multiples=errores), 400)

    return filtros


def validar_crear_reserva(datos: dict) -> dict:
    """
    PRE CONDICIONES: Recibe el diccionario del payload del request POST /reservas.
    POST CONDICIONES: Devuelve los datos listos o eleva un ValueError con 400 acumulando inconsistencias.
    """
    if not isinstance(datos, dict) or not datos:
        raise ValueError(
            construir_error_api(
                code=ERROR_CODE_INVALID_BODY,
                message="El cuerpo de la solicitud es inválido",
                level="error",
                description="Se esperaba un objeto JSON no vacío en el cuerpo de la solicitud",
            ),
            400,
        )

    errores = []

    # 1. Campos obligatorios
    campos_requeridos = [
        "id_socio",
        "id_cancha",
        "fecha_hora_inicio",
        "fecha_hora_fin",
    ]
    for campo in campos_requeridos:
        if campo not in datos or datos[campo] is None:
            errores.append(
                {
                    "code": f"required.{campo}",
                    "message": "El cuerpo de la solicitud es inválido",
                    "level": "error",
                    "description": f"El campo '{campo}' es obligatorio",
                }
            )

    # validación de ids usando validar_id
    for campo in ["id_socio", "id_cancha"]:
        valor = datos.get(campo)
        if valor is not None:
            try:
                validar_id(valor)
            except ValueError:
                errores.append(
                    {
                        "code": ERROR_CODE_INVALID_PARAM,
                        "message": "El cuerpo de la solicitud es inválido",
                        "level": "error",
                        "description": f"El campo '{campo}' debe ser un número entero positivo mayor a cero",
                    }
                )

    #validación de fechas ISO 8601 GMT-3
    inicio_valido, fin_valido = False, False
    inicio, fin = None, None

    for campo_fecha in ["fecha_hora_inicio", "fecha_hora_fin"]:
        val_fecha = datos.get(campo_fecha)
        if val_fecha:
            str_fecha = str(val_fecha).strip()
            if not ISO_GMT3_REGEX.match(str_fecha):
                errores.append(
                    {
                        "code": ERROR_CODE_INVALID_FECHA,
                        "message": "El cuerpo de la solicitud es inválido",
                        "level": "error",
                        "description": f"El campo '{campo_fecha}' debe respetar el formato ISO 8601 con microsegundos y zona GMT-3 (ej: 2026-10-15T18:00:00.000000-03:00)",
                    }
                )
            else:
                try:
                    parsed_dt = datetime.fromisoformat(str_fecha)
                    if campo_fecha == "fecha_hora_inicio":
                        inicio = parsed_dt
                        inicio_valido = True
                    else:
                        fin = parsed_dt
                        fin_valido = True
                except ValueError:
                    errores.append(
                        {
                            "code": ERROR_CODE_INVALID_FECHA,
                            "message": "El cuerpo de la solicitud es inválido",
                            "level": "error",
                            "description": f"El campo '{campo_fecha}' no contiene una fecha/hora válida",
                        }
                    )

    if inicio_valido and fin_valido and inicio >= fin:
        errores.append(
            {
                "code": ERROR_CODE_INVALID_FECHA,
                "message": "El cuerpo de la solicitud es inválido",
                "level": "error",
                "description": "La 'fecha_hora_inicio' debe ser anterior a 'fecha_hora_fin'",
            }
        )

    if errores:
        raise ValueError(construir_error_api(errores_multiples=errores), 400)

    return datos


def validar_datos_actualizar_reserva(data: dict) -> dict:
    """
    PRE CONDICIONES: Recibe el diccionario del request PUT /reservas/<id>.
    POST CONDICIONES: Valida parcialmente las claves presentes y devuelve el diccionario refinado.
    """
    if not isinstance(data, dict) or not data:
        raise ValueError(
            construir_error_api(
                code=ERROR_CODE_INVALID_BODY,
                message="El cuerpo de la solicitud no puede estar vacío y debe ser un JSON válido",
                level="error",
                description="Se esperaba un objeto JSON en el cuerpo del request",
            ),
            400,
        )

    errores = []
    datos_limpios = {}

    if "id_cancha" in data and data["id_cancha"] is not None:
        try:
            datos_limpios["id_cancha"] = validar_id(data["id_cancha"])
        except ValueError:
            errores.append(
                {
                    "code": ERROR_CODE_INVALID_PARAM,
                    "message": "El campo 'id_cancha' es inválido",
                    "level": "error",
                    "description": f"Se recibió {data.get('id_cancha')}. Debe ser un número entero positivo",
                }
            )

    if "estado" in data and data["estado"] is not None:
        try:
            estado_str = validar_string_no_vacio(data["estado"], "estado").lower()
            if estado_str not in ESTADOS_PERMITIDOS:
                errores.append(
                    {
                        "code": ERROR_CODE_INVALID_PARAM,
                        "message": "El estado de la reserva es inválido",
                        "level": "error",
                        "description": f"Se recibió '{data.get('estado')}'. Valores permitidos: {', '.join(ESTADOS_PERMITIDOS)}",
                    }
                )
            else:
                datos_limpios["estado"] = estado_str
        except ValueError:
            errores.append(
                {
                    "code": ERROR_CODE_INVALID_PARAM,
                    "message": "El campo 'estado' no puede estar vacío",
                    "level": "error",
                    "description": "El campo 'estado' debe ser una cadena válida",
                }
            )

    inicio, fin = None, None
    inicio_valido, fin_valido = False, False

    if "fecha_hora_inicio" in data and data["fecha_hora_inicio"] is not None:
        str_inicio = str(data["fecha_hora_inicio"]).strip()
        if not ISO_GMT3_REGEX.match(str_inicio):
            errores.append(
                {
                    "code": ERROR_CODE_INVALID_FECHA,
                    "message": "El formato de 'fecha_hora_inicio' es inválido",
                    "level": "error",
                    "description": "Debe cumplir el estándar ISO 8601 con zona GMT-3 (ej: 2026-10-15T18:00:00.000000-03:00)",
                }
            )
        else:
            try:
                inicio = datetime.fromisoformat(str_inicio)
                datos_limpios["fecha_hora_inicio"] = str_inicio
                inicio_valido = True
            except ValueError:
                errores.append(
                    {
                        "code": ERROR_CODE_INVALID_FECHA,
                        "message": "Fecha inválida",
                        "level": "error",
                        "description": "'fecha_hora_inicio' no es una fecha u hora válida",
                    }
                )

    if "fecha_hora_fin" in data and data["fecha_hora_fin"] is not None:
        str_fin = str(data["fecha_hora_fin"]).strip()
        if not ISO_GMT3_REGEX.match(str_fin):
            errores.append(
                {
                    "code": ERROR_CODE_INVALID_FECHA,
                    "message": "El formato de 'fecha_hora_fin' es inválido",
                    "level": "error",
                    "description": "Debe cumplir el estándar ISO 8601 con zona GMT-3 (ej: 2026-10-15T18:00:00.000000-03:00)",
                }
            )
        else:
            try:
                fin = datetime.fromisoformat(str_fin)
                datos_limpios["fecha_hora_fin"] = str_fin
                fin_valido = True
            except ValueError:
                errores.append(
                    {
                        "code": ERROR_CODE_INVALID_FECHA,
                        "message": "Fecha inválida",
                        "level": "error",
                        "description": "'fecha_hora_fin' no es una fecha u hora válida",
                    }
                )

    if inicio_valido and fin_valido and inicio >= fin:
        errores.append(
            {
                "code": ERROR_CODE_INVALID_FECHA,
                "message": "Rango de horarios incoherente",
                "level": "error",
                "description": "'fecha_hora_inicio' debe ser anterior a 'fecha_hora_fin'",
            }
        )

    if errores:
        raise ValueError(construir_error_api(errores_multiples=errores), 400)

    return datos_limpios


def validar_cambiar_estado_reserva(data: dict) -> dict:
    """
    PRE CONDICIONES: Recibe el diccionario del request PUT/PATCH /reservas/<id>/estado.
    POST CONDICIONES: Devuelve el estado limpio o eleva ValueError con 400.
    """
    if not isinstance(data, dict) or not data:
        raise ValueError(
            construir_error_api(
                code=ERROR_CODE_INVALID_BODY,
                message="El cuerpo de la solicitud es inválido",
                level="error",
                description="Se esperaba un objeto JSON no vacío en el cuerpo de la solicitud",
            ),
            400,
        )

    try:
        estado_str = validar_string_no_vacio(data.get("estado"), "estado").lower()
    except ValueError:
        raise ValueError(
            construir_error_api(
                code="required.estado",
                message="El cuerpo de la solicitud es inválido",
                level="error",
                description="El campo 'estado' es obligatorio y no puede estar vacío",
            ),
            400,
        )

    if estado_str not in ESTADOS_PERMITIDOS:
        raise ValueError(
            construir_error_api(
                code=ERROR_CODE_INVALID_PARAM,
                message="El estado de la reserva es inválido",
                level="error",
                description=f"Se recibió '{estado_str}'. Los valores permitidos son: {', '.join(ESTADOS_PERMITIDOS)}",
            ),
            400,
        )

    return {"estado": estado_str}