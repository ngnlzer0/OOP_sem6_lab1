# app/dao/car_dao.py
from app.DAO.base_dao import BaseDAO
from app.models.car import PassengerCar, CargoCar
import psycopg


class CarDAO(BaseDAO):
    def get_all(self):
        query = """
            SELECT c.id, c.model, c.type, c.condition, c.fuel_level, 
                   p.seats, cg.load_capacity
            FROM car c
            LEFT JOIN passenger_car p ON c.id = p.car_id
            LEFT JOIN cargo_car cg ON c.id = cg.car_id
        """
        cars = []
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                for row in cur.fetchall():
                    # row mapping: 0:id, 1:model, 2:type, 3:cond, 4:fuel, 5:seats, 6:load
                    if row[2] == 'passenger':
                        cars.append(PassengerCar(row[0], row[1], row[3], row[4], row[5]))
                    elif row[2] == 'cargo':
                        cars.append(CargoCar(row[0], row[1], row[3], row[4], row[6]))
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