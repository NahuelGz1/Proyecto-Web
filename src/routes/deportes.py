from flask import Blueprint, jsonify
from src.services.deportes import obtener_deportes
from src.utils import procesar_error_api

deportes_bp = Blueprint('deportes', __name__)


@deportes_bp.route('/', methods=['GET'])
def get_deportes():
    try:
        deportes = obtener_deportes()

        if not deportes:
            return '', 204

        return jsonify({"deportes": deportes}), 200
    except Exception as e:
        payload, status = procesar_error_api(e)
        return jsonify(payload), status