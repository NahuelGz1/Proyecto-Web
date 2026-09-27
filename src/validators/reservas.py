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
            id_socio_val = int(id_socio)
            if id_socio_val <= 0:
                errores.append(
                    {
                        "code": "PARAM_INVALIDO",
                        "message": "Parámetro inválido",
                        "level": "error",
                        "description": "El parámetro 'id_socio' debe ser un número entero positivo mayor a 0",
                    }
                )
            else:
                filtros["id_socio"] = id_socio_val
        except ValueError:
            errores.append(
                {
                    "code": "PARAM_INVALIDO",
                    "message": "Parámetro inválido",
                    "level": "error",
                    "description": "El parámetro 'id_socio' debe ser un número entero válido",
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



def validar_crear_reserva(datos: dict) -> dict:
    """
    Valida el cuerpo JSON para el endpoint POST /reservas
    acumulando errores según la especificación de Swagger.
    """
    errores = []


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



def validar_datos_actualizar_reserva(data: dict) -> dict:
    if not data or not isinstance(data, dict):
        payload = construir_error_api(
            code="CUERPO_INVALIDO",
            message="El cuerpo de la solicitud no puede estar vacío y debe ser un JSON válido",
            description="Se esperaba un objeto JSON en el cuerpo del request",
        )
        raise ValueError(payload, 400)

    errores = []
    datos_limpios = {}

    #  Validar id_cancha
    if "id_cancha" in data:
        try:
            datos_limpios["id_cancha"] = int(str(data["id_cancha"]).strip())
        except ValueError:
            errores.append(
                {
                    "code": "PARAMETRO_INVALIDO",
                    "message": "El campo 'id_cancha' debe ser un número entero",
                    "level": "error",
                    "description": f"Se recibió {data.get('id_cancha')}",
                }
            )

    #  Validar estado
    if "estado" in data:
        estado = str(data["estado"]).strip().lower()
        if estado not in ("confirmada", "cancelada", "finalizada"):
            errores.append(
                {
                    "code": "PARAMETRO_INVALIDO",
                    "message": "El estado de la reserva es inválido",
                    "level": "error",
                    "description": f"Se recibió '{data.get('estado')}'. Valores permitidos: confirmada, cancelada, finalizada",
                }
            )
        else:
            datos_limpios["estado"] = estado

    #  Validar fechas/horas si se envían en el PUT (formato: YYYY-MM-DD HH:MM:SS)
    inicio = None
    fin = None

    if "fecha_hora_inicio" in data:
        try:
            inicio = datetime.strptime(
                str(data["fecha_hora_inicio"]).strip(), "%Y-%m-%d %H:%M:%S"
            )
            datos_limpios["fecha_hora_inicio"] = data[
                "fecha_hora_inicio"
            ].strip()
        except ValueError:
            errores.append(
                {
                    "code": "PARAMETRO_INVALIDO",
                    "message": "El formato de 'fecha_hora_inicio' es inválido",
                    "level": "error",
                    "description": "Debe seguir el formato 'YYYY-MM-DD HH:MM:SS'",
                }
            )

    if "fecha_hora_fin" in data:
        try:
            fin = datetime.strptime(
                str(data["fecha_hora_fin"]).strip(), "%Y-%m-%d %H:%M:%S"
            )
            datos_limpios["fecha_hora_fin"] = data["fecha_hora_fin"].strip()
        except ValueError:
            errores.append(
                {
                    "code": "PARAMETRO_INVALIDO",
                    "message": "El formato de 'fecha_hora_fin' es inválido",
                    "level": "error",
                    "description": "Debe seguir el formato 'YYYY-MM-DD HH:MM:SS'",
                }
            )

    if inicio and fin and inicio >= fin:
        errores.append(
            {
                "code": "PARAMETRO_INVALIDO",
                "message": "Rango de horarios incoherente",
                "level": "error",
                "description": "'fecha_hora_inicio' debe ser anterior a 'fecha_hora_fin'",
            }
        )

    # Si hay errores acumulados, corta el flujo con 400
    if errores:
        payload = construir_error_api(errores_multiples=errores)
        raise ValueError(payload, 400)

    return datos_limpios


