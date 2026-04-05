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

    def complete_trip(self, trip_id, car_condition):
        """Завершує рейс і оновлює стан авто"""
        # Розбиваємо на три окремі запити
        query1 = "UPDATE trip SET is_completed = true, finished_at = NOW() WHERE id = %s"

        query2 = """
            UPDATE request SET status = 'completed' 
            WHERE id = (SELECT request_id FROM trip WHERE id = %s)
        """

        query3 = """
            UPDATE car SET condition = %s 
            WHERE id = (SELECT car_id FROM driver WHERE id = (SELECT driver_id FROM trip WHERE id = %s))
        """

        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # Виконуємо їх по черзі
                cur.execute(query1, (trip_id,))
                cur.execute(query2, (trip_id,))
                cur.execute(query3, (car_condition, trip_id))

                # І тільки після цього зберігаємо всі зміни разом
                conn.commit()

    def create_trip_by_car(self, request_id, car_id):
        """Створює рейс, автоматично знаходячи водія за вибраним авто"""
        query = """
            INSERT INTO trip (request_id, driver_id)
            SELECT %s, id FROM driver WHERE car_id = %s
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (request_id, car_id))
                conn.commit()

    def get_all_trips_history(self):
        """Отримує повну історію всіх рейсів для журналу"""
        query = """
            SELECT t.id, r.destination, u.login as driver_name, c.model as car_model, 
                   t.is_completed, t.finished_at
            FROM trip t
            JOIN request r ON t.request_id = r.id
            JOIN driver d ON t.driver_id = d.id
            JOIN "user" u ON d.user_id = u.id
            JOIN car c ON d.car_id = c.id
            ORDER BY t.id DESC
        """
        history = []
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                for row in cur.fetchall():
                    history.append({
                        'id': row[0],
                        'destination': row[1],
                        'driver': row[2],
                        'car': row[3],
                        'is_completed': row[4],
                        'finished_at': row[5].strftime('%Y-%m-%d %H:%M') if row[5] else 'В процесі'
                    })
        return history