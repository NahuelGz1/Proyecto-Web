from src.repositories.canchas import contar_canchas, listar_canchas, obtener_cancha_por_id
from src.validators.canchas import validar_filtros_canchas, validar_paginacion


def obtener_listado_canchas(args):
    filtros = validar_filtros_canchas(args)
    limit, offset = validar_paginacion(args)

    total = contar_canchas(filtros)
    canchas = listar_canchas(filtros, limit, offset)

    return canchas, total, limit, offset


def obtener_cancha(cancha_id):
    return obtener_cancha_por_id(cancha_id)


def registrar_cancha(body: dict) -> dict:
    return


def actualizar_cancha(cancha_id: int, body: dict) -> None:
    pass

def borrar_cancha(cancha_id: int) -> None:
    pass


def obtener_canchas_disponibles(args: dict) -> tuple[list[dict], int, int, int]:
    pass