from flask import Blueprint, jsonify, request
from src.services.reservas import (
    obtener_listado_reservas,
    obtener_reserva,
    crear_nueva_reserva
)
from src.utils import generar_links_paginacion, procesar_error_api
from src.validators.reservas import validar_reserva_post

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

        #valida la estructura y tipos de datos en la capa de validadores
        datos_validados = validar_reserva_post(datos)

        #llama al servicio para la lógica de negocio y persistencia
        nueva_reserva = crear_nueva_reserva(datos_validados)

        #retorna la respuesta exitosa 201 Created
        return jsonify(nueva_reserva), 201

    except Exception as e:
        payload, status = procesar_error_api(e)
        return jsonify(payload), status