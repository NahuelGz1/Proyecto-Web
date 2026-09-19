



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
            description=f"El campo '{nombre}' es obligatorio y no puede estar vacio"
        ))

    return str(valor).strip()