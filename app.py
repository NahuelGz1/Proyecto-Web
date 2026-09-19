from flask import Flask
from src.constants import BASE_URL

# se importan los blueprints a mano a medida que los creemos
from src.routes.deportes import deportes_bp
from src.routes.socios import socios_bp

app = Flask(__name__)
app.json.ensure_ascii = False

# registra blueprints asociandoles la base_url
app.register_blueprint(deportes_bp, url_prefix=BASE_URL)
app.register_blueprint(socios_bp, url_prefix=BASE_URL)

@app.route('/')
def index():
    return {"estado": "ok", "mensaje": "API Servidor Base Activo"}, 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)