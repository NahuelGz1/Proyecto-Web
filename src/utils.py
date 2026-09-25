import re

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


def convertir_booleanos(datos: dict | list[dict] | None, campos: list[str]) -> dict | list[dict] | None:

    if datos is None:
        return None

    if isinstance(datos, list):
        return [convertir_booleanos(item, campos) for item in datos]

    for campo in campos:
        if campo in datos and datos[campo] is not None:
            datos[campo] = bool(datos[campo])

    return datos

def convertir_booleanos_cancha(cancha: dict) -> dict:
    return convertir_booleanos(cancha, ["techada", "activa"])

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
