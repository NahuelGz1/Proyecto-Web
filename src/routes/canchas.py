from flask import Blueprint, jsonify, request
from src.services.canchas import (
    actualizar_cancha,
    borrar_cancha,
    obtener_cancha,
    obtener_canchas_disponibles,
    obtener_listado_canchas,
    registrar_cancha,
)

canchas_bp = Blueprint('canchas', __name__)


# funcion auxiliar (por eso el _ al principio de la funcion)para armar los links de paginacion
# si tenes 100 canchas y pedis de a 10, esta funcion te calcula y te arma los links para ir a la pagina siguiente, anterior, primera y ultima
def _generar_links_paginacion(total: int, limit: int, offset: int) -> dict:
    url_base = request.host_url.rstrip('/') + request.path
    filtros_url = [
        f"{clave}={valor}"
        for clave, valor in request.args.items()
        if clave not in ("_limit", "_offset")
    ]
    query_string = "&".join(filtros_url)
    prefijo = f"{url_base}?{query_string}&" if query_string else f"{url_base}?"
    ultimo_offset = max((total - 1) // limit, 0) * limit if total > 0 else 0

    return {
        "_first": {"href": f"{prefijo}_offset=0&_limit={limit}"},
        "_prev": (
            {"href": f"{prefijo}_offset={max(offset - limit, 0)}&_limit={limit}"}
            if offset > 0
            else None
        ),
        "_next": (
            {"href": f"{prefijo}_offset={offset + limit}&_limit={limit}"}
            if offset + limit < total
            else None
        ),
        "_last": {"href": f"{prefijo}_offset={ultimo_offset}&_limit={limit}"},
    }


# trae la lista general de canchas
# por ejemplo: GET /canchas?techada=true te trae solo las canchas techadas
# si no encuentra nada responde 204 sin contenido, si hay canchas te devuelve la lista paginada
@canchas_bp.route('/canchas', methods=['GET'])
def get_canchas():
    canchas, total, limit, offset = obtener_listado_canchas(request.args)
    if not canchas:
        return '', 204

    links = _generar_links_paginacion(total, limit, offset)
    return jsonify({"canchas": canchas, "_links": links}), 200


# trae unicamente las canchas que estan libres para alquilar
@canchas_bp.route("/canchas/disponibles", methods=["GET"])
def get_canchas_disponibles():
    canchas, total, limit, offset = obtener_canchas_disponibles(request.args)
    links = _generar_links_paginacion(total, limit, offset)
    return jsonify({"canchas": canchas, "_links": links}), 200


# busca una sola cancha segun el numero de id
# por ejemplo: GET /canchas/5 te devuelve toda la data de la cancha numero 5
@canchas_bp.route('/canchas/<int:cancha_id>', methods=['GET'])
def get_cancha_por_id(cancha_id):
    cancha = obtener_cancha(cancha_id)
    return jsonify(cancha), 200


# crea una cancha nueva en el sistema
# recibe los datos en formato json, crea la cancha y te devuelve el objeto creado con estado 201 y la cabecera Location apuntando a la nueva cancha
@canchas_bp.route("/canchas", methods=["POST"])
def post_cancha():
    data = request.get_json(silent=True)
    cancha = registrar_cancha(data)
    headers = {"Location": f"/canchas/{cancha['id']}"}
    return jsonify(cancha), 201, headers


# modifica algunos datos de una cancha existente
# por ejemplo: mandas PATCH /canchas/2 con {"precio": 2500} y solo cambia el precio de esa cancha
@canchas_bp.route("/canchas/<int:cancha_id>", methods=["PATCH"])
def patch_cancha(cancha_id: int):
    data = request.get_json(silent=True)
    actualizar_cancha(cancha_id, data)
    cancha = obtener_cancha(cancha_id)
    return jsonify(cancha), 200


# borra una cancha del sistema usando su id
# si sale tod bien responde con un status 204 sin contenido
@canchas_bp.route("/canchas/<int:cancha_id>", methods=["DELETE"])
def delete_cancha(cancha_id: int):
    borrar_cancha(cancha_id)
    return "", 204