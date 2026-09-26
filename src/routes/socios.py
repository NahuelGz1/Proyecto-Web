from flask import Blueprint, jsonify, request, url_for
from sqlalchemy.exc import IntegrityError
from src.services.socios import (
    actualizar_socio_por_id,
    crear_socio,
    obtener_socio_por_id,
    obtener_socios,
)
from src.utils import construir_error_api

socios_bp = Blueprint('socios', __name__)


# funcion auxiliar para construir las urls de paginacion
# si pedis socios paginados, te genera los links para navegar entre paginas manteniendo los filtros de nombre y si esta activo
def _generar_enlace(nombre, activo, limit, offset):
    return url_for(
        'socios.get_socios',
        nombre=nombre,
        activo=activo,
        _limit=limit,
        _offset=offset,
    )


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
    limit = request.args.get('_limit', 10, type=int)
    offset = request.args.get('_offset', 0, type=int)
    nombre = request.args.get('nombre')
    activo = request.args.get('activo')

    socios, total = obtener_socios(nombre, activo, limit, offset)

    if not socios:
        return '', 204

    ult_offset = max(((total - 1) // limit) * limit, 0) if total > 0 else 0

    enlaces = {
        "_first": {"href": _generar_enlace(nombre, activo, limit, 0)},
        "_prev": (
            {"href": _generar_enlace(nombre, activo, limit, max(0, offset - limit))}
            if offset > 0
            else None
        ),
        "_next": (
            {"href": _generar_enlace(nombre, activo, limit, offset + limit)}
            if offset + limit < total
            else None
        ),
        "_last": {"href": _generar_enlace(nombre, activo, limit, ult_offset)},
    }

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
@socios_bp.route('/socios/<int:id>', methods=['GET'])
def get_socio(id: int):
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
@socios_bp.route('/socios/<int:id>', methods=['PATCH'])
def actualizar_socio(id: int):
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