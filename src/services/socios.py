from src.repositories.socios import (
    listar_socios,
    buscar_socio_por_id,
    insertar_socio,
    actualizar_socio_en_base,
    contar_socios,
)

from src.utils import (
    validar_booleano,
    validar_string_no_vacio,
    validar_email,
    construir_error_api,
    validar_id,
    validar_paginacion,
)


# aplica validaciones sobre parametros de busqueda/paginacion y trae la lista de socios
def obtener_socios(args: dict):
    limit, offset = validar_paginacion(args)

    nombre = args.get("nombre")

    activo_raw = args.get("activo")
    if activo_raw is not None:
        activo_raw = (
            activo_raw.lower() == "true"
            if isinstance(activo_raw, str)
            else bool(activo_raw)
        )

    activo = validar_booleano(activo_raw, nombre="activo", default=None)

    filtros = {"nombre": nombre, "activo": activo}


    total = contar_socios(filtros)
    if total == 0:
        return None, 0, limit, offset


    socios = listar_socios(filtros, limit, offset)

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