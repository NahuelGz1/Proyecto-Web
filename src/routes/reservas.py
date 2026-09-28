from flask import Blueprint, jsonify, request

from src.services.reservas import (
    actualizar_reserva,
    cambiar_estado_reserva,
    crear_reserva,
    listar_reservas,
    obtener_reserva_por_id,
)
from src.utils import (
    generar_links_paginacion,
    procesar_error_api,
    validar_id,
    validar_paginacion,
)
from src.validators.reservas import (
    validar_cambiar_estado_reserva,
    validar_crear_reserva,
    validar_datos_actualizar_reserva,
    validar_filtros_reservas,
)

reservas_bp = Blueprint("reservas", __name__)


@reservas_bp.route("/", methods=["GET"])
def obtener_reservas_route():
    try:
        limit, offset = validar_paginacion(request.args)
        filtros = validar_filtros_reservas(request.args)

        reservas, total = listar_reservas(
            filtros=filtros, limit=limit, offset=offset
        )
        links = generar_links_paginacion(total, limit, offset)

        return jsonify({"data": reservas, "_links": links}), 200
    except Exception as e:
        payload, status = procesar_error_api(e)
        return jsonify(payload), status


@reservas_bp.route("/", methods=["POST"])
def crear_reserva_route():
    try:
        datos = validar_crear_reserva(request.get_json())
        reserva_creada = crear_reserva(datos)
        return jsonify(reserva_creada), 201
    except Exception as e:
        payload, status = procesar_error_api(e)
        return jsonify(payload), status


@reservas_bp.route("/<id_reserva>", methods=["GET"])
def obtener_reserva_por_id_route(id_reserva):
    try:
        id_valido = validar_id(id_reserva)
        reserva = obtener_reserva_por_id(id_valido)
        return jsonify(reserva), 200
    except Exception as e:
        payload, status = procesar_error_api(e)
        return jsonify(payload), status


@reservas_bp.route("/<id_reserva>", methods=["PUT"])
def actualizar_reserva_route(id_reserva):
    try:
        id_valido = validar_id(id_reserva)
        datos = validar_datos_actualizar_reserva(request.get_json())
        reserva_actualizada = actualizar_reserva(id_valido, datos)
        return jsonify(reserva_actualizada), 200
    except Exception as e:
        payload, status = procesar_error_api(e)
        return jsonify(payload), status


@reservas_bp.route("/<int:id_reserva>/estado", methods=["PUT", "PATCH"])
def cambiar_estado(id_reserva):
    try:
        data = request.get_json() or {}

        datos_validados = validar_cambiar_estado_reserva(data)

        nuevo_estado = datos_validados["estado"]

        cambiar_estado_reserva(id_reserva, nuevo_estado)

        return "", 204

    except Exception as e:
        return procesar_error_api(e)