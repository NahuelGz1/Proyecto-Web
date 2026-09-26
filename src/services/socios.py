from src.repositories.socios import (
    listar_socios,
    buscar_socio_por_id,
    insertar_socio,
    actualizar_socio_en_base,
)
from src.utils import (
    validar_limit,
    validar_no_negativo,
    validar_booleano,
    validar_string_no_vacio,
    validar_email,
    construir_error_api,
)


# aplica validaciones sobre parametros de busqueda/paginacion y trae la lista de socios
# por ejemplo: obtener_socios(nombre="Juan", activo=True, limit=10, offset=0)
def obtener_socios(nombre, activo, limit, offset):
    limit = validar_limit(limit, 'limit')
    offset = validar_no_negativo(offset, 'offset')
    activo = validar_booleano(activo, 'activo', default=None)

    filtros = {"nombre": nombre, "activo": activo}
    return listar_socios(filtros, limit, offset)


# valida el cuerpo recibido e inserta un nuevo socio activo
# por ejemplo: crear_socio({"nombre": "Juan Perez", "email": "juan@gmail.com"}) retorna el socio con su id
def crear_socio(datos: dict) -> dict:
    if not datos:
        raise ValueError(
            construir_error_api(
                code="invalid_request",
                message="Solicitud inválida",
                description="No se recibieron datos para crear el socio",
            ),
            400,
        )

    nombre = validar_string_no_vacio(datos.get('nombre'), 'nombre')
    email = validar_email(datos.get('email'))
    activo = True

    nuevo_id = insertar_socio(nombre, email, activo)

    return {
        'id': nuevo_id,
        'nombre': nombre,
        'email': email,
        'activo': activo,
    }


# obtiene un unico socio mediante su id
# por ejemplo: obtener_socio_por_id(1) devuelve {"id": 1, "nombre": "Juan", ...} o None
def obtener_socio_por_id(id_socio: int):
    return buscar_socio_por_id(id_socio)


# actualiza parcialmente los datos de un socio existente validando solo los campos enviados
# por ejemplo: actualizar_socio_por_id(1, {"email": "nuevo@gmail.com"}) actualiza el email si el socio existe
def actualizar_socio_por_id(id_socio: int, datos: dict) -> bool:
    socio = buscar_socio_por_id(id_socio)
    if not socio:
        return False

    datos_verificados = {}

    if 'nombre' in datos:
        datos_verificados['nombre'] = validar_string_no_vacio(
            datos.get('nombre'), 'nombre'
        )
    if 'email' in datos:
        datos_verificados['email'] = validar_email(datos.get('email'))
    if 'activo' in datos:
        datos_verificados['activo'] = validar_booleano(
            datos.get('activo'), 'activo', default=socio['activo']
        )

    if datos_verificados:
        actualizar_socio_en_base(id_socio, datos_verificados)

    return True