import os
import psycopg2
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# Define a string de conexão usando as variáveis de ambiente
DATABASE_URL = (
    f"dbname='{os.getenv('DB_NAME')}' "
    f"user='{os.getenv('DB_USER')}' "
    f"host='{os.getenv('DB_HOST')}' "
    f"password='{os.getenv('DB_PASS')}' "
    f"port='{os.getenv('DB_PORT')}'"
)

def get_db_connection():
    """Cria e retorna uma nova conexão com o banco de dados."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except psycopg2.OperationalError as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None