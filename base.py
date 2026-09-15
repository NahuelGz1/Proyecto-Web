import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def conexion():
    connection = mysql.connector.connect(
        host=os.getenv('DB_HOST', '127.0.0.1'), # getenv va a buscar los datos de su archivo .env, si no encuentra reemplaza por los otros datos
        user=os.getenv('DB_USER', 'alumno'),
        password=os.getenv('DB_PASSWORD', '1234'),
        database=os.getenv('DB_NAME', 'club_deportivo'),
        port=int(os.getenv('DB_PORT', 3306))
    )
    return connection