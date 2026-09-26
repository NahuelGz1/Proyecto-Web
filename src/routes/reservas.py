from flask import Blueprint, jsonify, request
from src.services.reservas import obtener_listado_reservas
from src.utils import generar_links_paginacion

reservas_bp = Blueprint("reservas", __name__)




@reservas_bp.route("/reservas", methods=["GET"])
def get_reservas():
    resultado = obtener_listado_reservas(request.args)

    # 1. Caso sin contenido -> 204
    if resultado is None:
        return "", 204

    reservas, total, limit, offset = resultado

    links = generar_links_paginacion(total, limit, offset)

    respuesta = {"reservas": reservas, "_links": links}

    return jsonify(respuesta), 200