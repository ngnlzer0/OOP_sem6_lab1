# app/dao/trip_dao.py
from app.DAO.base_dao import BaseDAO

class TripDAO(BaseDAO):
    def create_trip(self, request_id, driver_id):
        query = """
            INSERT INTO trip (request_id, driver_id, is_completed, started_at)
            VALUES (%s, %s, FALSE, NOW()) RETURNING id
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (request_id, driver_id))
                trip_id = cur.fetchone()[0]
                conn.commit()
                return trip_id