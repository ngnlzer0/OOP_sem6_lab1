import psycopg

class TripDAO:
    def __init__(self, db_url):
        self.db_url = db_url

    def get_connection(self):
        return psycopg.connect(self.db_url)

    def get_driver_trips(self, user_id):
        """Отримує активні рейси для водія на основі його user_id"""
        query = """
            SELECT t.id, r.destination, r.required_type, r.required_value
            FROM trip t
            JOIN request r ON t.request_id = r.id
            JOIN driver d ON t.driver_id = d.id
            WHERE d.user_id = %s AND t.is_completed = false
        """
        trips = []
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (user_id,))
                for row in cur.fetchall():
                    trips.append({
                        'id': row[0],
                        'destination': row[1],
                        'required_type': row[2],
                        'required_value': row[3]
                    })
        return trips