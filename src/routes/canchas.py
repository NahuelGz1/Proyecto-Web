from flask import Blueprint, jsonify, request
from src.services.canchas import (
    actualizar_cancha,
    borrar_cancha,
    obtener_cancha,
    obtener_canchas_disponibles,
    obtener_listado_canchas,
    registrar_cancha,
)
from src.utils import generar_links_paginacion, procesar_error_api

canchas_bp = Blueprint('canchas', __name__)


# Listado general de canchas
@canchas_bp.route('/', methods=['GET'])
def get_canchas():
    try:
        canchas, total, limit, offset = obtener_listado_canchas(request.args)
        if not canchas:
            return '', 204

        links = generar_links_paginacion(total, limit, offset)
        return jsonify({"canchas": canchas, "_links": links}), 200
    except Exception as e:
        payload, status = procesar_error_api(e)
        return jsonify(payload), status


# Canchas disponibles
@canchas_bp.route("/disponibles", methods=["GET"])
def get_canchas_disponibles():
    try:
        canchas, total, limit, offset = obtener_canchas_disponibles(request.args)
        links = generar_links_paginacion(total, limit, offset)
        return jsonify({"canchas": canchas, "_links": links}), 200
    except Exception as e:
        payload, status = procesar_error_api(e)
        return jsonify(payload), status


# Detalle de cancha por ID
@canchas_bp.route('/<cancha_id>', methods=['GET'])
def get_cancha_por_id(cancha_id):
    try:
        cancha = obtener_cancha(cancha_id)
        return jsonify(cancha), 200
    except Exception as e:
        payload, status = procesar_error_api(e)
        return jsonify(payload), status


# Alta de nueva cancha
@canchas_bp.route("/", methods=["POST"])
def post_cancha():
    try:
        data = request.get_json(silent=True)
        cancha = registrar_cancha(data)
        headers = {"Location": f"/canchas/{cancha['id']}"}
        return jsonify(cancha), 201, headers
    except Exception as e:
        payload, status = procesar_error_api(e)
        return jsonify(payload), status


# Modificación parcial (PATCH)
@canchas_bp.route("/<cancha_id>", methods=["PATCH"])
def patch_cancha(cancha_id):
    try:
        data = request.get_json(silent=True)
        actualizar_cancha(cancha_id, data)
        return '', 204
    except Exception as e:
        payload, status = procesar_error_api(e)
        return jsonify(payload), status


# Eliminación permanente
@canchas_bp.route("/<cancha_id>", methods=["DELETE"])
def delete_cancha(cancha_id):
    try:
        borrar_cancha(cancha_id)
        return "", 204
    except Exception as e:
        payload, status = procesar_error_api(e)
        return jsonify(payload), status