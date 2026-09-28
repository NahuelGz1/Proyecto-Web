from src.repositories.socios import (
    actualizar_socio_en_base,
    buscar_socio_por_id,
    contar_socios,
    insertar_socio,
    listar_socios,
)

from src.utils import (
    construir_error_api,
    validar_booleano,
    validar_email,
    validar_id,
    validar_paginacion,
    validar_string_no_vacio,
)


# aplica validaciones sobre parametros de busqueda/paginacion y trae la lista de socios
def obtener_socios(args: dict):
    limit, offset = validar_paginacion(args)

    nombre = args.get("nombre")

    # manejo del booleano que viene como string desde los query params
    activo_raw = args.get("activo")
    if activo_raw is not None:
        activo_raw = activo_raw.lower() == 'true' if isinstance(activo_raw, str) else bool(activo_raw)

    activo = validar_booleano(activo_raw, 'activo', default=None)

    filtros = {"nombre": nombre, "activo": activo}

    # obtenemos la lista y el total por separado
    socios = listar_socios(filtros, limit, offset)
    total = contar_socios(filtros)

    # retornamos los 4 valores para el unpacking del blueprint
    return socios, total, limit, offset


# valida el cuerpo recibido e inserta un nuevo socio activo
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
def obtener_socio_por_id(id_socio):
    id_socio = validar_id(id_socio)
    return buscar_socio_por_id(id_socio)


# actualiza parcialmente los datos de un socio existente validando solo los campos enviados
def actualizar_socio_por_id(id_socio, datos: dict) -> bool:
    id_socio = validar_id(id_socio)

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