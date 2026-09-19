class ValidationError(Exception):
    """Excepción personalizada para errores de validación en la solicitud."""
    pass


def validar_filtros_canchas(args):
    id_deporte = args.get('id_deporte', type=int)
    nombre = args.get('nombre', type=str)
    techada = args.get('techada', type=str)
    activa = args.get('activa', type=str)

    if techada is not None and techada.lower() not in ("true", "false"):
        raise ValidationError("El parámetro techada debe ser true o false")

    if activa is not None and activa.lower() not in ("true", "false"):
        raise ValidationError("El parámetro activa debe ser true o false")

    return {
        "id_deporte": id_deporte,
        "nombre": nombre,
        "techada": techada.lower() == "true" if techada is not None else None,
        "activa": activa.lower() == "true" if activa is not None else None,
    }


def validar_paginacion(args):
    try:
        limit = int(args.get('_limit', 10))
        offset = int(args.get('_offset', 0))
    except ValueError:
        raise ValidationError("_limit y _offset deben ser números enteros")

    if not (1 <= limit <= 100) or offset < 0:
        raise ValidationError("_limit debe estar entre 1 y 100, y _offset no puede ser negativo")

    return limit, offset