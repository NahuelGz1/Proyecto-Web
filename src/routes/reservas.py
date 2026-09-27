from flask import Blueprint, jsonify, request
from src.services.reservas import (
    obtener_listado_reservas,
    obtener_reserva,
    crear_nueva_reserva, modificar_reserva
)
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


@reservas_bp.route("/reservas/<int:id>", methods=["GET"])
def get_reserva_por_id(id: int):
    try:
        reserva = obtener_reserva(id)
        return jsonify(reserva), 200
    except Exception as e:
        payload, status = procesar_error_api(e)
        return jsonify(payload), status


@reservas_bp.route("/reservas", methods=["POST"])
def post_reserva():
    try:
        datos = request.get_json() or {}

        # Pasa el JSON crudo. El servicio valida y crea.
        nueva_reserva = crear_nueva_reserva(datos)

        headers = {"Location": f"/reservas/{nueva_reserva['id']}"}
        return jsonify(nueva_reserva), 201, headers

    except Exception as e:
        payload, status = procesar_error_api(e)
        return jsonify(payload), status


@reservas_bp.route("/reservas/<int:id_reserva>", methods=["PUT"])
def put_reserva(id_reserva):
    try:
        body = request.get_json(silent=True)
        reserva_actualizada = modificar_reserva(id_reserva, body)
        return jsonify(reserva_actualizada), 200

    except Exception as e:
        payload, status = procesar_error_api(e)
        return jsonify(payload), status

