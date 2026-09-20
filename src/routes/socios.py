from flask import Blueprint, jsonify, request
import mysql.connector
from src.services.socios import obtener_socios
from flask import Blueprint, jsonify, request, url_for

socios_bp = Blueprint('socios', __name__)

def enlace(nombre, activo, limit, offset):
    return url_for('socios.get_socios',nombre=nombre,activo=activo,_limit=limit,_offset=offset)

@socios_bp.route('/socios', methods=['GET'])
def get_socios():

    limit = int(request.args.get('_limit', 10))
    offset = int(request.args.get('_offset', 0))
    nombre = request.args.get('nombre')
    activo = request.args.get('activo')

    socios, total = obtener_socios(nombre,activo,limit,offset)

    if not socios:
        return '', 204

    ult_offset = ((total - 1) // limit) * limit
    prev_offset = max(0, offset - limit)

    if offset + limit < total:
        sig_offset = offset + limit
    else:
        sig_offset = ult_offset

    enlaces = {
        "_first": {
            "href": enlace(nombre, activo, limit, 0)
        },
        "_prev": {
            "href": enlace(nombre, activo, limit, prev_offset)
        },
        "_next": {
            "href": enlace(nombre, activo, limit, sig_offset)
        },
        "_last": {
            "href": enlace(nombre, activo, limit, ult_offset)
        }
    }

    return jsonify({"socios": socios, "_links": enlaces}), 200