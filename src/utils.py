import re

from src.constants import ERROR_CODE_INVALID_PARAM


def construir_error_api(code: str, message: str, description: str, level: str = 'error') -> dict:
    """Construye un payload de error compatible con el resto de la API."""
    return {
        'errors': [{
            'code': code,
            'message': message,
            'level': level,
            'description': description
        }]
    }

CAMPOS_BOOLEANOS = {"techada", "activa", "activo", "es_socio", "bloqueado"}

def _convertir_dict_booleano(d: dict) -> dict:
    """convierte valores 0 y 1 a true y false para las claves booleanas"""
    res = d.copy()
    for clave, valor in res.items():
        if clave in CAMPOS_BOOLEANOS and valor is not None:
            res[clave] = bool(valor)
    return res


def convertir_booleanos(datos):
    """procesa un solo diccionario o una lista de diccionarios unificando booleanos"""
    if datos is None:
        return None

    if isinstance(datos, list):
        return [_convertir_dict_booleano(item) for item in datos]

    if isinstance(datos, dict):
        return _convertir_dict_booleano(datos)

    return datos

def validar_string_no_vacio(valor, nombre: str) -> str:
    if valor is None or not str(valor).strip():
        raise ValueError(construir_error_api(
            code=f'required.{nombre}',
            message=f"Campo requerido: '{nombre}'",
            level='error',
            description=f"El campo '{nombre}' es obligatorio y no puede estar vacio"
        ))

    return str(valor).strip()


def validar_positivo(valor,nombre: str) -> int:
    if valor is None or valor <=0:
        raise ValueError(construir_error_api(
            code = 'invalid_numero',
            message = 'valor incompatible',
            level = 'error',
            description = 'El numero no es positivo'

        ))
    return valor

def validar_mayor_a_uno(valor, nombre: str) -> int:
    if valor is None or valor <= 1:
        raise ValueError(construir_error_api(
            code = 'invalid_numero',
            message = 'valor incompatible',
            level = 'error',
            description = 'El numero no es mayor a uno'
            
        ))
    return valor

def validar_booleano(valor, nombre: str, default: bool) -> bool:
    if valor is None:
        return default

    if valor is not True and valor is not False:
        raise ValueError(construir_error_api(
            code=f'invalid.{nombre}',
            message=f"Campo inválido: '{nombre}'",
            level='error',
            description=f"El campo '{nombre}' debe ser true o false"
        ))

    return valor

def validar_no_negativo(valor, nombre: str) -> int:
    if valor is None or valor < 0:
        raise ValueError(construir_error_api(
            code ='invalid_numero',
            message ='valor incompatible',
            level ='error',
            description ='El numero es negativo'
        ))
    return valor

def validar_limit(valor, nombre: str) -> int:
    if valor < 1 or valor > 100:
        raise ValueError(construir_error_api(
            code='invalid_numero',
            message='valor incompatible',
            level='error',
            description='El parametro _limit debe ser un numero entre 1 y 100'
        ))

    return valor

def validar_email(email: str) -> str:
    email_limpio = validar_string_no_vacio(email, 'email')
    patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(patron, email_limpio):
        raise ValueError(construir_error_api(
            code='invalid.email',
            message='Formato de email inválido',
            level='error',
            description="El campo 'email' debe ser una dirección de correo válida"
        ))
        
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