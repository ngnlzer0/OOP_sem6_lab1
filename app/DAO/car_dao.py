# app/dao/car_dao.py
from app.DAO.base_dao import BaseDAO
from app.models.car import PassengerCar, CargoCar
import psycopg


class CarDAO(BaseDAO):
    def get_all_cars(self):
        """Отримує всі авто з усією інформацією для сторінки автопарку"""
        query = """
            SELECT c.id, c.model, c.type, c.fuel_level, c.condition,
                   pc.seats, cc.load_capacity
            FROM car c
            LEFT JOIN passenger_car pc ON c.id = pc.car_id
            LEFT JOIN cargo_car cc ON c.id = cc.car_id
            ORDER BY c.id ASC
        """
        cars = []
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                for row in cur.fetchall():
                    cars.append({
                        'id': row[0],
                        'model': row[1],
                        'type': 'Пасажирський' if row[2] == 'passenger' else 'Вантажний',
                        'fuel_level': row[3],
                        'condition': row[4],
                        'capacity': f"{row[5]} місць" if row[2] == 'passenger' else f"{row[6]} кг"
                    })
        return cars

    def update_condition(self, car_id, condition):
        """Приклад маніпуляції даними (Update) через SQL """
        query = "UPDATE car SET condition = %s WHERE id = %s"
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (condition, car_id))
                conn.commit()

    def create_car(self, model, car_type, fuel_level, capacity):
        # RETURNING id дозволяє нам одразу отримати згенерований ID нового авто
        query_car = "INSERT INTO car (model, type, fuel_level) VALUES (%s, %s, %s) RETURNING id"

        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # 1. Записуємо в базову таблицю car
                cur.execute(query_car, (model, car_type, fuel_level))
                new_car_id = cur.fetchone()[0]

                # 2. Залежно від типу, записуємо специфічні дані у відповідну таблицю
                if car_type == 'passenger':
                    query_sub = "INSERT INTO passenger_car (car_id, seats) VALUES (%s, %s)"
                    cur.execute(query_sub, (new_car_id, int(capacity)))
                elif car_type == 'cargo':
                    query_sub = "INSERT INTO cargo_car (car_id, load_capacity) VALUES (%s, %s)"
                    cur.execute(query_sub, (new_car_id, float(capacity)))

                conn.commit()

    def get_cars_for_assignment(self, req_type, req_value):
        """Шукає справні авто потрібного типу, які мають водія і підходять за місткістю"""
        query = """
            SELECT c.id, c.model, u.login as driver_name
            FROM car c
            JOIN driver d ON c.id = d.car_id
            JOIN "user" u ON d.user_id = u.id
            LEFT JOIN passenger_car pc ON c.id = pc.car_id
            LEFT JOIN cargo_car cc ON c.id = cc.car_id
            WHERE c.condition = true 
              AND c.type = %s
              AND (
                  (c.type = 'passenger' AND pc.seats >= %s) OR 
                  (c.type = 'cargo' AND cc.load_capacity >= %s)
              )
        """
        valid_cars = []
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (req_type, req_value, req_value))
                for row in cur.fetchall():
                    valid_cars.append({
                        'id': row[0],
                        'model': row[1],
                        'driver_name': row[2]
                    })
        return valid_cars