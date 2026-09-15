from flask import Flask, jsonify
import mysql.connector
from base import conexion

app = Flask(__name__)
app.json.ensure_ascii = False # esto es para que se pueda detectar los acentos a la hora de imprimir

@app.route('/deportes', methods=['GET']) # decorador, vincula el url /deportes con la funcion de abajo
def get_deportes():
    connection = None
    cursor = None
    try:
        connection = conexion() # intenta establecer conexion con los datos de base
        cursor = connection.cursor(dictionary=True) # crea cursor en la base de datos 
        
        cursor.execute("SELECT id, nombre FROM deportes ORDER BY id ASC;")
        deportes = cursor.fetchall() # lista de diccionarios
        
        if not deportes:
            return '', 204 # por si la lista esta vacia, 204 no content
        
        return jsonify({"deportes": deportes}), 200 # lista con deportes, devuelta como json

    except mysql.connector.Error as db_err:
        print(f"Error en la BD: {db_err}")
        error_response = {
            "errors": [
                {
                    "code": "DATABASE_ERROR",
                    "message": "Error al consultar la base de datos",
                    "level": "error",
                    "description": str(db_err)
                }
            ]
        }
        return jsonify(error_response), 500 # error del servidor 

    except Exception as e:
        print(f"Error inesperado: {e}")
        error_response = {
            "errors": [
                {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "Ocurrió un error inesperado en el servidor",
                    "level": "error",
                    "description": str(e)
                }
            ]
        }
        return jsonify(error_response), 500

    finally: # se ejecuta independientemente de si hubo exception o no
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)