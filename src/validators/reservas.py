from src.constants import ERROR_CODE_INVALID_PARAM
from src.utils import construir_error_api

#esta funcion valida los filtros que se pueden pasar por query params a la ruta de reservas, es mas que nada para
#lo que es el postman cuando colocas la ruta y le pasas los query params, para que no rompa la aplicacion y devuelva un error 400 con el mensaje correspondiente
def validar_filtros_reservas(args: dict) -> dict:
    """
    PRE CONDICIONES:
    POST CONDICIONES: devuelve un diccionario con los filtros validados para las reservas.
    Si no hay filtros devuelve un diccionario vacio
    """
    filtros = {}

    id_cancha = args.get("id_cancha")
    if id_cancha:
        filtros["id_cancha"] = int(id_cancha)

    id_socio = args.get("id_socio")
    if id_socio:
        filtros["id_socio"] = int(id_socio)

    estado = args.get("estado")
    if estado:
        filtros["estado"] = estado.strip().lower()

    fecha = args.get("fecha_desde")
    if fecha:
        filtros["fecha_desde"] = fecha.strip().lower()

    fecha = args.get("fecha_hasta")
    if fecha:
        filtros["fecha_hasta"] = fecha.strip().lower()

    return filtros



