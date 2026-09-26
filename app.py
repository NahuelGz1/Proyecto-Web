from flask import Flask, jsonify
from src.constants import BASE_URL, ERROR_CODE_INTERNAL
from src.utils import construir_error_api

from src.routes.deportes import deportes_bp
from src.routes.socios import socios_bp
from src.routes.canchas import canchas_bp



# arrancamos la aplicacion de flask
# el ensure_ascii en false es para que no rompa las letras con tildes o la enie
app = Flask(__name__)
app.json.ensure_ascii = False


# MANEJO GLOBAL DE ERRORES



# manejador global de errores de validacion
# cuando salta algun problema esperado en el sistema, esta funcion lo atrapa al vuelo
# por ejemplo: si querian crear una cancha sin nombre, la validacion falla y esta funcion se encarga de devolver el error en formato json con su codigo 400

@app.errorhandler(ValueError)
def manejar_value_error(error):
    """captura las excepciones de validación lanzadas por las utils/servicios"""
    status = error.args[1] if len(error.args) > 1 else 400
    return jsonify(error.args[0]), status



# manejador de errores raros o no esperados
# si pasa algo grave que no teniamos planeado (por ejemplo, se cayo la base de datos o fallos de conexion), esto evita que la app explote y le manda un error 500 empaquetado al cliente

@app.errorhandler(Exception)
def manejar_error_inesperado(error):
    """Captura cualquier error 500 no controlado."""
    print(f"Error inesperado: {error}")
    payload = construir_error_api(
        code=ERROR_CODE_INTERNAL,
        message="Ocurrió un error inesperado en el servidor",
        description=str(error)
    )
    return jsonify(payload), 500


# REGISTRO DE BLUEPRINTS

app.register_blueprint(deportes_bp, url_prefix=BASE_URL)
app.register_blueprint(socios_bp, url_prefix=BASE_URL)
app.register_blueprint(canchas_bp, url_prefix=BASE_URL)



# un endpoint simple en la raiz para probar que el servidor este vivo

@app.route('/')
def index():
    return {"estado": "ok", "mensaje": "API Servidor Base Activo"}, 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)