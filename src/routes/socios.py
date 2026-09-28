from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from src.services.socios import (
    actualizar_socio_por_id,
    crear_socio,
    obtener_socio_por_id,
    obtener_socios,
)
from src.utils import construir_error_api, generar_links_paginacion

socios_bp = Blueprint('socios', __name__)


# manejador local para mails duplicados en la base de datos
# si al crear o actualizar un socio pones un mail que ya existe, sqlalchemy lanza IntegrityError y esta funcion devuelve automaticamente el error 409
@socios_bp.errorhandler(IntegrityError)
def manejar_integridad_db(error):
    error409 = construir_error_api(
        code='email.already.exists',
        message='Conflicto de datos',
        description='El correo electrónico indicado ya pertenece a otro socio',
    )
    return jsonify(error409), 409


# trae el listado de socios filtrado y paginado
# por ejemplo: GET /socios?nombre=Juan&_limit=5 trae los primeros 5 socios que se llamen Juan
# si no hay resultados devuelve 204 sin contenido
@socios_bp.route('/socios', methods=['GET'])
def get_socios():
    socios, total, limit, offset = obtener_socios(request.args)

    if not socios:
        return '', 204

    enlaces = generar_links_paginacion(total, limit, offset)

    return jsonify({"socios": socios, "_links": enlaces}), 200


# da de alta a un socio nuevo
# recibe el json con los datos del socio y te devuelve el socio creado con codigo 201
@socios_bp.route('/socios', methods=['POST'])
def alta_socio():
    datos = request.get_json(silent=True)
    nuevo_socio = crear_socio(datos)
    return jsonify(nuevo_socio), 201


# busca la informacion de un solo socio por su id
# por ejemplo: GET /socios/12 devuelve los datos del socio 12, o 404 si no existe
@socios_bp.route('/socios/<id>', methods=['GET'])
def get_socio(id):
    socio = obtener_socio_por_id(id)

    if socio is None:
        error404 = construir_error_api(
            code='socio.not.found',
            message='Socio no encontrado',
            level='error',
            description=f'No existe un socio con id {id}',
        )
        return jsonify(error404), 404

    return jsonify(socio), 200


# modifica datos de un socio existente
# por example: PATCH /socios/5 enviando {"activo": false} desactiva a ese socio
@socios_bp.route('/socios/<id>', methods=['PATCH'])
def actualizar_socio(id):
    datos = request.get_json(silent=True)
    actualizacion = actualizar_socio_por_id(id, datos)

    if not actualizacion:
        error404 = construir_error_api(
            code='socio.not.found',
            message='Socio no encontrado',
            level='error',
            description=f'El socio {id} no existe',
        )
        return jsonify(error404), 404

    return "", 204