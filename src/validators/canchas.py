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

def validar_cancha_create(data):
        if not data:
            raise ValidationError("El pedido no puede estar vacío")
        
        CAMPOS_PERMITIDOS_CREATE = {"nombre", "id_deporte", "precio_hora", "techada", "activa"}
        campos_desconocidos = set(data.keys()) - CAMPOS_PERMITIDOS_CREATE
        if campos_desconocidos:
            raise ValidationError(f"Campos desconocidos: {', '.join(campos_desconocidos)}")
        
        nombre = data.get("nombre")
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValidationError("El nombre es obligatorio y no puede estar vacío")
        
        id_deporte = data.get("id_deporte")
        if not isinstance(id_deporte, int) or isinstance(id_deporte, bool):
            raise ValidationError("id_deporte es obligatorio y debe ser un entero")

        precio_hora = data.get("precio_hora")
        if not isinstance(precio_hora, int) or isinstance(precio_hora, bool) or precio_hora <= 0:
            raise ValidationError("precio_hora es obligatorio y debe ser un entero positivo")

        techada = data.get("techada", False)
        if not isinstance(techada, bool):
            raise ValidationError("techada debe ser true o false")

        activa = data.get("activa", True)
        if not isinstance(activa, bool):
            raise ValidationError("activa debe ser true o false")

        return {

            "nombre": nombre.strip(),
            "id_deporte": id_deporte,
            "precio_hora": precio_hora,
            "techada": techada,
            "activa": activa,

        }


        