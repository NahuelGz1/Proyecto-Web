from datetime import datetime
from src.repositories.reservas import (
    obtener_todas_las_reservas,
    obtener_reserva_por_id,
    obtener_datos_cancha,
    verificar_superposicion,
    guardar_reserva,
    modificar_estado_reserva
)
from src.constantes import (
    ERROR_CODE_CANCHA_NOT_FOUND,
    ERROR_CODE_HORARIO_OCUPADO,
    ERROR_CODE_TRANSICION_INVALIDA,
    ESTADO_CONFIRMADA,
    ESTADO_CANCELADA,
    ESTADO_FINALIZADA
)