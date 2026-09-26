from flask import Blueprint, jsonify
from src.services.deportes import obtener_deportes

deportes_bp = Blueprint('deportes', __name__)


# trae la lista completa de deportes disponibles en el sistema
# por ejemplo: GET /deportes te devuelve {"deportes": [{"id": 1, "nombre": "Futbol"}, {"id": 2, "nombre": "Tenis"}]}
# si la tabla esta vacia te responde con un status 204 sin contenido
@deportes_bp.route('/deportes', methods=['GET'])
def get_deportes():
    deportes = obtener_deportes()

    if not deportes:
        return '', 204

    return jsonify({"deportes": deportes}), 200