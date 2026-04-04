# app/dao/car_dao.py
from app.DAO.base_dao import BaseDAO
from app.models.car import PassengerCar, CargoCar

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