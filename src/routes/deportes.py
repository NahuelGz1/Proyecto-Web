from flask import Blueprint, jsonify
import mysql.connector
from src.services.deportes import obtener_deportes

deportes_bp = Blueprint('deportes', __name__)


@deportes_bp.route('/deportes', methods=['GET'])
def get_deportes():
    """
    Se encarga de conseguir la lista completa de deportes disponibles en el sistema.

    Precondiciones:
        - Ninguna (no necesita parámetros de entrada ni validaciones de cuerpo).
    Postcondiciones:
        - 200 OK: Retorna JSON con el arreglo de deportes si existen registros.
        - 204 No Content: Retorna respuesta vacía si la tabla no posee datos.
        - 500 Internal Server Error: Retorna un objeto con la estructura de error si falla la BD o el servidor.
    """
    try:
        # Se deja la lógica de obtención directamente a la capa de servicios
        deportes = obtener_deportes()

        # Si la lista vuelve vacía, se responde con 204 sin cuerpo
        if not deportes:
            return '', 204

        return jsonify({"deportes": deportes}), 200

    except mysql.connector.Error as db_err:
        # Captura fallos de la BD para evitar respuestas genéricas incompletas
        print(f"Error en la BD: {db_err}")
        return jsonify({
            "errors": [{
                "code": "DATABASE_ERROR",
                "message": "Error al consultar la base de datos",
                "level": "error",
                "description": str(db_err)
            }]
        }), 500

    except Exception as e:
        # Captura preventiva ante cualquier fallo insospechado fuera de la BD
        print(f"Error inesperado: {e}")
        return jsonify({
            "errors": [{
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Ocurrió un error inesperado en el servidor",
                "level": "error",
                "description": str(e)
            }]
        }), 500