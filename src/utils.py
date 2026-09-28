import re
from flask import request
from src.constants import ERROR_CODE_INTERNAL, ERROR_CODE_INVALID_PARAM

# ESTANDARIZACION DE PAGINACION

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

def validar_paginacion(args: dict):
    if "limit" in args or "offset" in args:
        raise ValueError(
            construir_error_api(
                code=ERROR_CODE_INVALID_PARAM,
                message="Parámetro inválido",
                description="'limit' y 'offset' están mal escritos, deben ser '_limit' y '_offset'"
            ),
            400
        )
    try:
        limit = int(args.get("_limit", 10))
        offset = int(args.get("_offset", 0))
    except ValueError:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_INVALID_PARAM,
            message="Parámetro inválido",
            description="limit y offset deben ser números enteros"
        ),
            400
        )
    if not (1 <= limit <= 100) or offset < 0:
        raise ValueError(construir_error_api(
            code=ERROR_CODE_INVALID_PARAM,
            message="Parámetro inválido",
            description="limit debe estar entre 1 y 100, y offset no puede ser negativo"
        ),
            400
        )
    return limit, offset

# CONSTRUCTORES Y MANEJADORES DE ERRORES API

def construir_error_api(code: str = None, message: str = None, description: str = None, level: str = 'error', errores_multiples: list = None) -> dict:
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

def _convertir_dict_booleano(d: dict) -> dict:
    res = d.copy()
    for clave, valor in res.items():
        if clave in CAMPOS_BOOLEANOS and valor is not None:
            res[clave] = bool(valor)
    return res

def convertir_booleanos(datos):
    if datos is None:
        return None
    if isinstance(datos, list):
        return [_convertir_dict_booleano(item) for item in datos]
    if isinstance(datos, dict):
        return _convertir_dict_booleano(datos)
    return datos

# VALIDACIONES REUTILIZABLES

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
def validar_positivo(valor, nombre: str) -> int:
    try:
        val_num = int(valor)
        if val_num <= 0:
            raise ValueError()
        return val_num
    except (ValueError, TypeError):
        raise ValueError(
            construir_error_api(
                code='invalid_numero',
                message='Valor incompatible',
                level='error',
                description=f"El campo '{nombre}' debe ser un número entero positivo mayor a cero"
            ),
            400
        )

def validar_mayor_a_uno(valor, nombre: str) -> float:
    try:
        val_num = float(valor)
        if val_num <= 0:
            raise ValueError()
        return val_num
    except (ValueError, TypeError):
        raise ValueError(
            construir_error_api(
                code='invalid_numero',
                message='Valor incompatible',
                level='error',
                description=f"El campo '{nombre}' debe ser un número positivo"
            ),
            400
        )

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

def validar_id(id):
    try:
        id_num = int(id)
        if id_num <= 0:
            raise ValueError()
        return id_num
    except (ValueError, TypeError):
        raise ValueError(
            construir_error_api(
                code="invalid_id",
                message="ID inválido",
                level="error",
                description="El ID debe ser un número entero positivo",
            ),
            400,
        )