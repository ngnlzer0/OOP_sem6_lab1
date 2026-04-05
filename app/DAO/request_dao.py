from app.DAO.base_dao import BaseDAO
from app.models.request import Request

class RequestDAO(BaseDAO):
    def get_all_pending(self):
        """Отримання всіх нових заявок [cite: 20]"""
        query = "SELECT id, required_type, required_value, destination, status FROM request WHERE status = 'pending'"
        requests = []
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                for row in cur.fetchall():
                    requests.append(Request(row[0], row[1], row[2], row[3], row[4]))
        return requests

    def create_request(self, required_type, required_value, destination):
        """Створення нової заявки в БД"""
        query = """
            INSERT INTO request (required_type, required_value, destination, status, created_at)
            VALUES (%s, %s, %s, 'pending', NOW())
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (required_type, required_value, destination))
                conn.commit()

    def update_status(self, req_id, new_status):
        """Змінює статус заявки (наприклад, на 'assigned' або 'completed')"""
        query = "UPDATE request SET status = %s WHERE id = %s"
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (new_status, req_id))
                conn.commit()