from flask import Blueprint, jsonify, request
from src.services.canchas import (
    actualizar_cancha,
    borrar_cancha,
    obtener_cancha,
    obtener_canchas_disponibles,
    obtener_listado_canchas,
    registrar_cancha,
)
from src.utils import generar_links_paginacion

canchas_bp = Blueprint('canchas', __name__)


# obtiene el listado general de canchas aplicando filtros y paginacion
# por ejemplo: GET /canchas?techada=true responde 200 con la lista paginada o 204 si esta vacia
@canchas_bp.route('/canchas', methods=['GET'])
def get_canchas():
    canchas, total, limit, offset = obtener_listado_canchas(request.args)
    if not canchas:
        return '', 204

    links = generar_links_paginacion(total, limit, offset)
    return jsonify({"canchas": canchas, "_links": links}), 200


# consulta y devuelve unicamente las canchas disponibles para un rango de fecha/hora
# por ejemplo: GET /canchas/disponibles?fecha=2026-10-15&hora_inicio=18:00&hora_fin=19:00
@canchas_bp.route("/canchas/disponibles", methods=["GET"])
def get_canchas_disponibles():
    canchas, total, limit, offset = obtener_canchas_disponibles(request.args)
    links = generar_links_paginacion(total, limit, offset)
    return jsonify({"canchas": canchas, "_links": links}), 200


# busca y retorna el detalle de una cancha especifica mediante su id
# por ejemplo: GET /canchas/5 devuelve los datos completos de la cancha 5
@canchas_bp.route('/canchas/<int:cancha_id>', methods=['GET'])
def get_cancha_por_id(cancha_id):
    cancha = obtener_cancha(cancha_id)
    return jsonify(cancha), 200


# registra una nueva cancha en la base de datos
# por ejemplo: POST /canchas crea la cancha y retorna status 201 junto al header Location
@canchas_bp.route("/canchas", methods=["POST"])
def post_cancha():
    data = request.get_json(silent=True)
    cancha = registrar_cancha(data)
    headers = {"Location": f"/canchas/{cancha['id']}"}
    return jsonify(cancha), 201, headers


# modifica parcialmente los atributos de una cancha existente (PATCH)
# por ejemplo: PATCH /canchas/2 con {"precio_hora": 2500} actualiza únicamente el precio
@canchas_bp.route("/canchas/<int:cancha_id>", methods=["PATCH"])
def patch_cancha(cancha_id: int):
    data = request.get_json(silent=True)
    actualizar_cancha(cancha_id, data)
    cancha = obtener_cancha(cancha_id)
    return jsonify(cancha), 200


# elimina permanentemente una cancha si no posee reservas asociadas
# por ejemplo: DELETE /canchas/3 retorna status 204 si la eliminacion fue exitosa
@canchas_bp.route("/canchas/<int:cancha_id>", methods=["DELETE"])
def delete_cancha(cancha_id: int):
    borrar_cancha(cancha_id)
    return "", 204