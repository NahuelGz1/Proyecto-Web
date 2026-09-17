import os
from dotenv import load_dotenv

load_dotenv()

# URL base de la API
BASE_URL = '/reserva_canchas_api'

# Formatos de fecha esperados
FORMATO_FECHA = '%Y-%m-%d'
FORMATO_FECHA_HORA = '%Y-%m-%d %H:%M:%S'

# Reglas de dominio del club
ESTADO_CONFIRMADA = 'confirmada'
ESTADO_CANCELADA = 'cancelada'
ESTADO_FINALIZADA = 'finalizada'

# Configuración de la base de datos (XAMPP / Docker)
DB_HOST     = os.getenv('DB_HOST', '127.0.0.1')
DB_PORT     = int(os.getenv('DB_PORT', '3306'))
DB_USER     = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME     = os.getenv('DB_NAME', 'reserva_canchas_club')
DB_URL      = f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Codigos de error
ERROR_CODE_INVALID_BODY        = 'invalid.body'
ERROR_CODE_INVALID_FECHA       = 'invalid.fecha'
ERROR_CODE_RESERVA_NOT_FOUND   = 'reserva.not.found'
ERROR_CODE_SOCIO_NOT_FOUND     = 'socio.not.found'
ERROR_CODE_CANCHA_NOT_FOUND    = 'cancha.not.found'
ERROR_CODE_HORARIO_OCUPADO     = 'horario.ocupado'
ERROR_CODE_TRANSICION_INVALIDA = 'transicion.estado.invalida'