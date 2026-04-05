import psycopg

class DriverDAO:
    def __init__(self, db_url):
        self.db_url = db_url

    def get_connection(self):
        return psycopg.connect(self.db_url)

    def get_unassigned_users(self):
        """Шукає користувачів з роллю driver, яких ще немає в таблиці driver"""
        query = """
            SELECT id, login FROM "user" 
            WHERE role = 'driver' AND id NOT IN (SELECT user_id FROM driver)
        """
        users = []
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                for row in cur.fetchall():
                    users.append({'id': row[0], 'login': row[1]})
        return users

    def get_available_cars(self):
        """Шукає авто, які ще не закріплені за жодним водієм"""
        query = """
            SELECT id, model, type FROM car 
            WHERE id NOT IN (SELECT car_id FROM driver)
        """
        cars = []
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                for row in cur.fetchall():
                    cars.append({'id': row[0], 'model': row[1], 'type': row[2]})
        return cars

    def link_driver(self, user_id, car_id, passport):
        """Створює запис у таблиці driver"""
        query = "INSERT INTO driver (user_id, car_id, passport) VALUES (%s, %s, %s)"
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (user_id, car_id, passport))
                conn.commit()