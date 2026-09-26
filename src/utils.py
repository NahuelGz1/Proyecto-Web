import re
from src.constants import ERROR_CODE_INTERNAL
from flask import request

# ESTANDARIZACION DE PAGINACION

# genera los hipervínculos de paginación (HATEOAS) de forma genérica para cualquier endpoint (canchas, reservas, socios, etc.)
# por ejemplo: genera los dicts _first, _prev, _next y _last manteniendo query params activos
def generar_links_paginacion(total: int, limit: int, offset: int) -> dict:
    url_base = request.host_url.rstrip('/') + request.path

    # preserva cualquier filtro que venga en los query params exceptuando los de paginación
    filtros_url = [
        f"{clave}={valor}"
        for clave, valor in request.args.items()
        if clave not in ("_limit", "_offset")
    ]

    query_string = "&".join(filtros_url)
    prefijo = f"{url_base}?{query_string}&" if query_string else f"{url_base}?"
    ultimo_offset = max((total - 1) // limit, 0) * limit if total > 0 else 0

    return {
        "_first": {"href": f"{prefijo}_offset=0&_limit={limit}"},
        "_prev": (
            {"href": f"{prefijo}_offset={max(offset - limit, 0)}&_limit={limit}"}
            if offset > 0
            else None
        ),
        "_next": (
            {"href": f"{prefijo}_offset={offset + limit}&_limit={limit}"}
            if offset + limit < total
            else None
        ),
        "_last": {"href": f"{prefijo}_offset={ultimo_offset}&_limit={limit}"},
    }


# CONSTRUCTORES Y MANEJADORES DE ERRORES API


# arma el formato json estandar para responder errores en la api
from src.constants import ERROR_CODE_INVALID_PARAM


def construir_error_api(code: str, message: str, description: str, level: str = 'error', errores_multiples: list = None) -> dict:
    if errores_multiples is not None:
        return {"errors": errores_multiples}
    return {
        'errors': [{
            'code': code,
            'message': message,
            'level': level,
            'description': description
        }]
    }


# procesa cualquier excepcion lanzada en la aplicacion
# si es un error de validacion (ValueError), extrae el json y el codigo de estado http (por defecto 400)
# si es un error no controlado, devuelve un error 500 estandar
def procesar_error_api(error: Exception):
    if isinstance(error, ValueError):
        status = error.args[1] if len(error.args) > 1 else 400
        return error.args[0], status

    print(f"Error inesperado: {error}")
    payload = construir_error_api(
        code=ERROR_CODE_INTERNAL,
        message="Ocurrió un error inesperado en el servidor",
        description=str(error)
    )
    return payload, 500


# CONVERSION DE TIPOS DE DATOS

CAMPOS_BOOLEANOS = {"techada", "activa", "activo", "es_socio", "bloqueado"}


# convierte 0 y 1 a verdaderos booleanos (true/false) en un diccionario
def _convertir_dict_booleano(d: dict) -> dict:
    """convierte valores 0 y 1 a true y false para las claves booleanas"""
    res = d.copy()
    for clave, valor in res.items():
        if clave in CAMPOS_BOOLEANOS and valor is not None:
            res[clave] = bool(valor)
    return res


# normaliza booleanos para respuestas individuales o listas de objetos
# por ejemplo: transforma {"activo": 1} en {"activo": True}
def convertir_booleanos(datos):
    """procesa un solo diccionario o una lista de diccionarios unificando booleanos"""
    if datos is None:
        return None

    if isinstance(datos, list):
        return [_convertir_dict_booleano(item) for item in datos]

    if isinstance(datos, dict):
        return _convertir_dict_booleano(datos)

    return datos


# VALIDACIONES REUTILIZABLES


# valida que un campo de texto no venga vacio ni lleno de espacios
# por ejemplo: "  Juan  " pasa a ser "Juan", pero "   " lanza error 400
def validar_string_no_vacio(valor, nombre: str) -> str:
    if valor is None or not str(valor).strip():
        raise ValueError(
            construir_error_api(
                code=f'required.{nombre}',
                message=f"Campo requerido: '{nombre}'",
                level='error',
                description=f"El campo '{nombre}' es obligatorio y no puede estar vacío"
            ),
            400
        )

    return str(valor).strip()


# valida que un numero sea estrictamente mayor a 0 (ejemplo: ids, precios)
def validar_positivo(valor, nombre: str) -> int:
    if valor is None or valor <= 0:
        raise ValueError(
            construir_error_api(
                code='invalid_numero',
                message='Valor incompatible',
                level='error',
                description=f"El campo '{nombre}' debe ser un número positivo"
            ),
            400
        )
    return valor


# valida que un numero sea estrictamente mayor a 1 (ejemplo: capacidad minima)
def validar_mayor_a_uno(valor, nombre: str) -> int:
    if valor is None or valor <= 1:
        raise ValueError(
            construir_error_api(
                code='invalid_numero',
                message='Valor incompatible',
                level='error',
                description=f"El campo '{nombre}' debe ser mayor a uno"
            ),
            400
        )
    return valor


# valida que el valor ingresado sea un booleano real (True o False)
# si el campo viene vacio (None), le asigna el valor por defecto indicado
def validar_booleano(valor, nombre: str, default: bool) -> bool:
    if valor is None:
        return default

    if valor is not True and valor is not False:
        raise ValueError(
            construir_error_api(
                code=f'invalid.{nombre}',
                message=f"Campo inválido: '{nombre}'",
                level='error',
                description=f"El campo '{nombre}' debe ser true o false"
            ),
            400
        )

    return valor


# valida que un numero sea mayor o igual a 0 (ejemplo: offset en paginacion)
def validar_no_negativo(valor, nombre: str) -> int:
    if valor is None or valor < 0:
        raise ValueError(
            construir_error_api(
                code='invalid_numero',
                message='Valor incompatible',
                level='error',
                description=f"El campo '{nombre}' no puede ser negativo"
            ),
            400
        )
    return valor


# valida que el limite de la paginacion este entre 1 y 100
def validar_limit(valor, nombre: str = "_limit") -> int:
    if valor < 1 or valor > 100:
        raise ValueError(
            construir_error_api(
                code='invalid_numero',
                message='Valor incompatible',
                level='error',
                description=f"El parámetro {nombre} debe ser un número entre 1 y 100"
            ),
            400
        )

    return valor


# valida que la cadena ingresada tenga formato de correo electronico valido
# por ejemplo: "usuario@dominio.com" pasa a minusculas y se valida
def validar_email(email: str) -> str:
    email_limpio = validar_string_no_vacio(email, 'email').lower()
    patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(patron, email_limpio):
        raise ValueError(
            construir_error_api(
                code='invalid.email',
                message='Formato de email inválido',
                level='error',
                description="El campo 'email' debe ser una dirección de correo válida"
            ),
            400
        )

    return email_limpio



def validar_paginacion(args: dict):

    try:
        limit = int(args.get("limit", 10))  #si limit en el diccionario args no existe, se asigna 10 por defecto
        offset = int(args.get("offset", 0)) #si offset en el diccionario args no existe, se asigna 0 por defecto
    except ValueError:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_INVALID_PARAM,
            message="Parámetro inválido",
            description="limit y offset deben ser números enteros"
        ))
    if not (1 <= limit <= 10) or offset < 0:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_INVALID_PARAM,
            message="Parámetro inválido",
            description="limit debe estar entre 1 y 10, y offset no puede ser negativo"
        ))
    return limit, offset