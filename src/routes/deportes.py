from flask import Blueprint, jsonify
import mysql.connector
from src.db import conexion

deportes_bp = Blueprint('deportes', __name__)

@deportes_bp.route('/deportes', methods=['GET'])
def get_deportes():
    conn = None
    cursor = None
    try:
        conn = conexion()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre FROM deportes ORDER BY id ASC;")
        deportes = cursor.fetchall()

        if not deportes:
            return '', 204

        return jsonify({"deportes": deportes}), 200

    except mysql.connector.Error as db_err:
        return jsonify({
            "errors": [
                {"code": "db.error", "message": str(db_err)}
            ]
        }), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()