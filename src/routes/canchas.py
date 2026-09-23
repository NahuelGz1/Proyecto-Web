from flask import Blueprint, jsonify, request
from src.services.canchas import obtener_listado_canchas, obtener_cancha, registrar_cancha, obtener_canchas_disponibles, actualizar_cancha

canchas_bp = Blueprint('canchas', __name__)


@canchas_bp.route('/canchas', methods=['GET'])
def get_canchas():
    try:
        canchas, total, limit, offset = obtener_listado_canchas(request.args)
    except ValueError as error:
        status = error.args[1] if len(error.args) > 1 else 400
        return jsonify(error.args[0]), status
    except Exception as error:
        print(f"Error inesperado: {error}")
        return jsonify({"errors": [{
            "code": "INTERNAL_SERVER_ERROR",
            "message": "Ocurrió un error inesperado en el servidor",
            "level": "error",
            "description": str(error)
        }]}), 500

    if not canchas:
        return '', 204

    url_base = request.host_url.rstrip('/') + request.path
    filtros_url = [f"{clave}={valor}" for clave, valor in request.args.items() if clave not in ("_limit", "_offset")]
    query_string = "&".join(filtros_url)
    prefijo = f"{url_base}?{query_string}&" if query_string else f"{url_base}?"
    ultimo_offset = max((total - 1) // limit, 0) * limit if total > 0 else 0

    links = {
        "_first": {"href": f"{prefijo}_offset=0&_limit={limit}"},
        "_prev": {"href": f"{prefijo}_offset={max(offset - limit, 0)}&_limit={limit}"} if offset > 0 else None,
        "_next": {"href": f"{prefijo}_offset={offset + limit}&_limit={limit}"} if offset + limit < total else None,
        "_last": {"href": f"{prefijo}_offset={ultimo_offset}&_limit={limit}"},
    }

    return jsonify({"canchas": canchas, "_links": links}), 200


@canchas_bp.route('/canchas/<int:cancha_id>', methods=['GET'])
def get_cancha_por_id(cancha_id):
    try:
        cancha = obtener_cancha(cancha_id)
    except ValueError as error:
        status = error.args[1] if len(error.args) > 1 else 400
        return jsonify(error.args[0]), status
    except Exception as error:
        print(f"Error inesperado: {error}")
        return jsonify({"errors": [{
            "code": "INTERNAL_SERVER_ERROR",
            "message": "Ocurrió un error inesperado en el servidor",
            "level": "error",
            "description": str(error)
        }]}), 500

    return jsonify(cancha), 200


@canchas_bp.route("/canchas", methods=["POST"])
def post_cancha():
    try:
        data = request.get_json(silent=True)
        cancha = registrar_cancha(data)
    except ValueError as error:
        status = error.args[1] if len(error.args) > 1 else 400
        return jsonify(error.args[0]), status
    except Exception as error:
        print(f"Error inesperado: {error}")
        return jsonify({"errors": [{
            "code": "INTERNAL_SERVER_ERROR",
            "message": "Ocurrió un error inesperado en el servidor",
            "level": "error",
            "description": str(error)
        }]}), 500

    return jsonify(cancha), 201

# 23/9 ----------------------------------------------------------------------------------- (PATCH)
#le llega el patch y llama a actualizar_cancha y envia codigos de error o valido si esta todo bien
@canchas_bp.route("/canchas/<int:cancha_id>", methods=["PATCH"])
def patch_cancha(cancha_id: int):
    try:
        data = request.get_json(silent=True)
        actualizar_cancha(cancha_id, data)
        cancha = obtener_cancha(cancha_id)
    except ValueError as error:
        status = error.args[1] if len(error.args) > 1 else 400
        return jsonify(error.args[0]), status
    except Exception as error:
        print(f"Error inesperado: {error}")
        return jsonify({"errors": [{
            "code": "INTERNAL_SERVER_ERROR",
            "message": "Ocurrió un error inesperado en el servidor",
            "level": "error",
            "description": str(error)
        }]}), 500

    return jsonify(cancha), 200


@canchas_bp.route("/canchas/<int:cancha_id>", methods=["DELETE"])
def delete_cancha(cancha_id: int):
    pass











@canchas_bp.route("/canchas/disponibles", methods=["GET"])
def get_canchas_disponibles():
    try:
        canchas, total, limit, offset = obtener_canchas_disponibles(request.args)
    except ValueError as error:
        status = error.args[1] if len(error.args) > 1 else 400
        return jsonify(error.args[0]), status
    except Exception as error:
        print(f"Error inesperado: {error}")
        return jsonify({"errors": [{
            "code": "INTERNAL_SERVER_ERROR",
            "message": "Ocurrió un error inesperado en el servidor",
            "level": "error",
            "description": str(error)
        }]}), 500


    # A diferencia de /canchas, aca siempre es 200, incluso con array vacio
    url_base = request.host_url.rstrip('/') + request.path
    filtros_url = [f"{clave}={valor}" for clave, valor in request.args.items() if clave not in ("_limit", "_offset")]
    query_string = "&".join(filtros_url)
    prefijo = f"{url_base}?{query_string}&" if query_string else f"{url_base}?"
    ultimo_offset = max((total - 1) // limit, 0) * limit if total > 0 else 0

    links = {
        "_first": {"href": f"{prefijo}_offset=0&_limit={limit}"},
        "_prev": {"href": f"{prefijo}_offset={max(offset - limit, 0)}&_limit={limit}"} if offset > 0 else None,
        "_next": {"href": f"{prefijo}_offset={offset + limit}&_limit={limit}"} if offset + limit < total else None,
        "_last": {"href": f"{prefijo}_offset={ultimo_offset}&_limit={limit}"},
    }

    return jsonify({"canchas": canchas, "_links": links}), 200