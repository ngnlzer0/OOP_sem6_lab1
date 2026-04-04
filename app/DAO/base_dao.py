import psycopg
from app.core.logger import log

class BaseDAO:
    def __init__(self, db_url):
        self.db_url = db_url

    def get_connection(self):
        try:
            return psycopg.connect(self.db_url)
        except Exception as e:
            log.error(f"Помилка підключення до БД: {e}")
            raise e