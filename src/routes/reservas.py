from flask import Blueprint, jsonify, request
from src.services.reservas import obtener_listado_reservas
from src.utils import generar_links_paginacion, procesar_error_api

reservas_bp = Blueprint("reservas", __name__)




@reservas_bp.route("/reservas", methods=["GET"])
def get_reservas():
    try:
        resultado = obtener_listado_reservas(request.args)
    except Exception as e:
        payload, status = procesar_error_api(e)
        return jsonify(payload), status


    if resultado is None:
        return "", 204

    reservas, total, limit, offset = resultado

    # Generamos los links
    links = generar_links_paginacion(total, limit, offset)

    # Respuesta 200
    return jsonify({"reservas": reservas, "_links": links}), 200