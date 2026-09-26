import re
from src.constants import ERROR_CODE_INTERNAL

# CONSTRUCTORES Y MANEJADORES DE ERRORES API


# arma el formato json estandar para responder errores en la api
def construir_error_api(code: str, message: str, description: str, level: str = 'error') -> dict:
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
    res = d.copy()
    for clave, valor in res.items():
        if clave in CAMPOS_BOOLEANOS and valor is not None:
            res[clave] = bool(valor)
    return res


# normaliza booleanos para respuestas individuales o listas de objetos
# por ejemplo: transforma {"activo": 1} en {"activo": True}
def convertir_booleanos(datos):
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