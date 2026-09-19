



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
    if (valor <= 0):
        raise ValueError(construir_error_api(
            code = 'invalid_numero',
            message = 'valor incompatible',
            level = 'error',
            description = 'El numero no es positivo'

        ))
    return valor

def validar_mayor_a_uno():
    return

def validar_verdadero():
    return

