from src.repositories.socios import listar_socios, buscar_socio_por_id, insertar_socio, actualizar_socio_en_base
from src.utils import validar_limit, validar_no_negativo, validar_booleano, validar_positivo, validar_string_no_vacio, validar_email


def obtener_socios(nombre, activo, limit, offset):
    limit= validar_limit(limit, 'limit')
    offset = validar_no_negativo(offset, 'offset')
    activo = validar_booleano(activo, 'activo', default=None)

    return listar_socios(nombre, activo, limit, offset)

def crear_socio(datos: dict) -> dict:
    if not datos:
        raise ValueError({
            "errors": [
                {
                    "code": "invalid_request",
                    "message": "Solicitud inválida",
                    "level": "error",
                    "description": "No se recibieron datos para crear el socio"
                }
            ]
        })
    nombre = validar_string_no_vacio(datos.get('nombre'), 'nombre')
    email = validar_email(datos.get('email'))
    activo = True
    nuevo_id = insertar_socio(nombre, email, activo)
    
    return {
        'id': nuevo_id,
        'nombre': nombre,
        'email': email,
        'activo': activo
    }

def obtener_socio_por_id(id):
    return buscar_socio_por_id(id)

def actualizar_socio_por_id(id: int, datos: dict) -> bool:
    socio = buscar_socio_por_id(id)
    if not socio:
        return False

    datos_verificados = {}

    if 'nombre' in datos:
        datos_verificados['nombre'] = validar_string_no_vacio(datos.get('nombre'), 'nombre')
    if 'email' in datos:
        datos_verificados['email'] = validar_email(datos.get('email'))
    if 'activo' in datos:
        datos_verificados['activo'] = validar_booleano(datos.get('activo'), 'activo', default=socio['activo'])

    if datos_verificados:
        actualizar_socio_en_base(id, datos_verificados)

    return True