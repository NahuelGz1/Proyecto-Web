from src.constants import ERROR_CODE_INVALID_PARAM
from src.utils import construir_error_api
from datetime import datetime

# esta funcion valida los filtros que se pueden pasar por query params a la ruta de reservas...
def validar_filtros_reservas(args: dict) -> dict:
    """
    PRE CONDICIONES:
    POST CONDICIONES: devuelve un diccionario con los filtros validados para las reservas.
    Si no hay filtros devuelve un diccionario vacio
    """
    filtros = {}
    errores = []

    id_cancha = args.get("id_cancha")
    if id_cancha:
        try:
            filtros["id_cancha"] = int(id_cancha)
        except ValueError:
            errores.append(
                {
                    "code":"PARAM_INVALIDO",
                    "message":"Parámetro inválido",
                    "level":"error",
                    "description":"El parámetro 'id_cancha' debe ser un número entero válido"
                }
            )

    id_socio = args.get("id_socio")
    if id_socio:
        try:
            filtros["id_socio"] = int(id_socio)
        except ValueError:
            errores.append(
                {
                    "code":"PARAM_INVALIDO",
                    "message":"Parámetro inválido",
                    "level":"error",
                    "description":"El parámetro 'id_socio' debe ser un número entero válido"
                }
            )

    estado = args.get("estado")
    if estado:
        estado_limpio = estado.strip().lower()
        if estado_limpio not in ("confirmada", "cancelada", "finalizada"):
            errores.append(
                {
                    "code":"PARAM_INVALIDO",
                    "message":"Parámetro inválido",
                    "level":"error",
                    "description":f"El parámetro 'estado' debe ser uno de los siguientes valores: 'confirmada', 'cancelada', 'finalizada'. Valor recibido: '{estado}'"
                }
            )
        else:
            filtros["estado"] = estado_limpio

    fecha_desde = args.get("fecha_desde")
    fecha_desde_valida = False
    if fecha_desde:
        try:
            datetime.strptime(fecha_desde.strip(), "%Y-%m-%d")
            filtros["fecha_desde"] = fecha_desde.strip()
            fecha_desde_valida = True
        except ValueError:
            errores.append(
                {
                    "code":"PARAM_INVALIDO",
                    "message":"Parámetro inválido",
                    "level":"error",
                    "description":f"El parámetro 'fecha_desde' debe tener el formato 'YYYY-MM-DD'. Valor recibido: '{fecha_desde}'"
                }
            )

    fecha_hasta = args.get("fecha_hasta")
    fecha_hasta_valida = False
    if fecha_hasta:
        try:
            datetime.strptime(fecha_hasta.strip(), "%Y-%m-%d")
            filtros["fecha_hasta"] = fecha_hasta.strip()
            fecha_hasta_valida = True
        except ValueError:
            errores.append(
                {
                    "code": "PARAMETRO_INVALIDO",
                    "message": "Parametro invalido",
                    "level": "error",
                    "description":f"El parámetro 'fecha_hasta' debe tener el formato 'YYYY-MM-DD'. Valor recibido: '{fecha_hasta}'"
                }
            )

    if fecha_desde_valida and fecha_hasta_valida:
        if filtros["fecha_desde"] > filtros["fecha_hasta"]:
            errores.append(
                {
                    "code": "PARAMETRO_INVALIDO",
                    "message": "Rango de fechas incoherente",
                    "level": "error",
                    "description": "'fecha_desde' no puede ser posterior a 'fecha_hasta'",
                }
            )

    if errores:
        payload_error = construir_error_api(errores_multiples=errores)
        raise ValueError(payload_error, 400)

    return filtros



def validar_reserva_post(datos: dict) -> dict:
    """
    Valida el cuerpo JSON para el endpoint POST /reservas
    acumulando errores según la especificación de Swagger.
    """
    errores = []

    #campos obligatorios
    campos_requeridos = [
        "id_socio", "id_cancha", "fecha_hora_inicio",
        "fecha_hora_fin", "precio_hora", "precio_total"
    ]
    for campo in campos_requeridos:
        if campo not in datos or datos[campo] is None:
            errores.append({
                "code": "ERROR_VALIDACION",
                "message": "El cuerpo de la solicitud es inválido",
                "level": "error",
                "description": f"El campo '{campo}' es obligatorio"
            })

    #validaciones de números enteros positivos
    for campo in ["precio_hora", "precio_total", "id_socio", "id_cancha"]:
        valor = datos.get(campo)
        if valor is not None and (not isinstance(valor, int) or valor <= 0):
            errores.append({
                "code": "ERROR_VALIDACION",
                "message": "El cuerpo de la solicitud es inválido",
                "level": "error",
                "description": f"El campo '{campo}' debe ser un entero mayor a cero"
            })

    #validaciones de fechas ISO
    inicio_valido = False
    fin_valido = False

    if datos.get("fecha_hora_inicio"):
        try:
            inicio = datetime.fromisoformat(datos["fecha_hora_inicio"])
            inicio_valido = True
        except (ValueError, TypeError):
            errores.append({
                "code": "ERROR_VALIDACION",
                "message": "El cuerpo de la solicitud es inválido",
                "level": "error",
                "description": "El campo 'fecha_hora_inicio' debe ser una fecha/hora en formato ISO 8601 válida"
            })

    if datos.get("fecha_hora_fin"):
        try:
            fin = datetime.fromisoformat(datos["fecha_hora_fin"])
            fin_valido = True
        except (ValueError, TypeError):
            errores.append({
                "code": "ERROR_VALIDACION",
                "message": "El cuerpo de la solicitud es inválido",
                "level": "error",
                "description": "El campo 'fecha_hora_fin' debe ser una fecha/hora en formato ISO 8601 válida"
            })

    if inicio_valido and fin_valido and inicio >= fin:
        errores.append({
            "code": "ERROR_VALIDACION",
            "message": "El cuerpo de la solicitud es inválido",
            "level": "error",
            "description": "La 'fecha_hora_inicio' debe ser anterior a 'fecha_hora_fin'"
        })

    if errores:
        payload_error = construir_error_api(errores_multiples=errores)
        raise ValueError(payload_error, 400)

    return datos