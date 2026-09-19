from flask import Blueprint, jsonify, request
import mysql.connector
from src.services.canchas import obtener_listado_canchas, obtener_cancha, crear_cancha_service
from src.validators.canchas import ValidationError

canchas_bp = Blueprint('canchas', __name__)


def _armar_respuesta_error(codigo, mensaje, descripcion=None):
    error = {"code": codigo, "message": mensaje, "level": "error"}
    if descripcion:
        error["description"] = descripcion
    return {"errors": [error]}


def _crear_link(url):
    return {"href": url} if url else None


@canchas_bp.route('/canchas', methods=['GET'])
def get_canchas():
    try:
        canchas, total, limit, offset = obtener_listado_canchas(request.args)

        if not canchas:
            return '', 204

        url_base = request.host_url.rstrip('/') + request.path

        filtros_url = []
        for clave, valor in request.args.items():
            if clave not in ("_limit", "_offset"):
                filtros_url.append(f"{clave}={valor}")

        query_string = "&".join(filtros_url)
        prefijo = f"{url_base}?{query_string}&" if query_string else f"{url_base}?"

        ultimo_offset = max((total - 1) // limit, 0) * limit if total > 0 else 0

        links = {
            "_first": _crear_link(f"{prefijo}_offset=0&_limit={limit}"),
            "_prev": _crear_link(f"{prefijo}_offset={max(offset - limit, 0)}&_limit={limit}") if offset > 0 else None,
            "_next": _crear_link(f"{prefijo}_offset={offset + limit}&_limit={limit}") if offset + limit < total else None,
            "_last": _crear_link(f"{prefijo}_offset={ultimo_offset}&_limit={limit}"),
        }

        return jsonify({"canchas": canchas, "_links": links}), 200

    except ValidationError as err_val:
        return jsonify(_armar_respuesta_error("INVALID_PARAM", str(err_val))), 400

    except mysql.connector.Error as db_err:
        print(f"Error en la BD: {db_err}")
        return jsonify(_armar_respuesta_error(
            "DATABASE_ERROR", "Error al consultar la base de datos", str(db_err)
        )), 500

    except Exception as err_inesperado:
        print(f"Error inesperado: {err_inesperado}")
        return jsonify(_armar_respuesta_error(
            "INTERNAL_SERVER_ERROR", "Ocurrió un error inesperado en el servidor", str(err_inesperado)
        )), 500


@canchas_bp.route('/canchas/<int:cancha_id>', methods=['GET'])
def get_cancha_por_id(cancha_id):
    try:
        cancha = obtener_cancha(cancha_id)

        if not cancha:
            return jsonify(_armar_respuesta_error(
                "NOT_FOUND", f"No se encontró la cancha con id {cancha_id}"
            )), 404

        return jsonify(cancha), 200

    except mysql.connector.Error as db_err:
        print(f"Error en la BD: {db_err}")
        return jsonify(_armar_respuesta_error(
            "DATABASE_ERROR", "Error al consultar la base de datos", str(db_err)
        )), 500

    except Exception as err_inesperado:
        print(f"Error inesperado: {err_inesperado}")
        return jsonify(_armar_respuesta_error(
            "INTERNAL_SERVER_ERROR", "Ocurrió un error inesperado en el servidor", str(err_inesperado)
        )), 500
    

@canchas_bp.route('/canchas', methods=['POST'])
def post_cancha():
    try:
        data = request.get_json(silent=True)
        cancha = crear_cancha_service(data)
        return jsonify(cancha), 201

    except ValidationError as err_val:
        return jsonify(_armar_respuesta_error("INVALID_PARAM", str(err_val))), 400

    except ValueError as err_val:
        return jsonify(_armar_respuesta_error("NOT_FOUND", str(err_val))), 404

    except mysql.connector.Error as db_err:
        print(f"Error en la BD: {db_err}")
        return jsonify(_armar_respuesta_error(
            "DATABASE_ERROR", "Error al consultar la base de datos", str(db_err)
        )), 500

    except Exception as err_inesperado:
        print(f"Error inesperado: {err_inesperado}")
        return jsonify(_armar_respuesta_error(
            "INTERNAL_SERVER_ERROR", "Ocurrió un error inesperado en el servidor", str(err_inesperado)
        )), 500