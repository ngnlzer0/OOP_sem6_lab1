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