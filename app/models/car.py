from app.core.logger import log

class Car:
    def __init__(self, id, model, car_type, condition=True, fuel_level=100):
        self.id = id
        self.model = model
        self.car_type = car_type
        self._condition = condition  # Protected поле
        self._fuel_level = fuel_level

    @property
    def is_ready(self):
        """Чи готове авто до виїзду загалом"""
        return self._condition and self._fuel_level > 10

    def validate_for_request(self, request):
        """Базовий метод для поліморфізму"""
        if not self.is_ready:
            return False
        return self.car_type == request.required_type

class PassengerCar(Car):
    def __init__(self, id, model, condition, fuel_level, seats):
        super().__init__(id, model, 'passenger', condition, fuel_level)
        self.seats = seats

    def validate_for_request(self, request):
        """Поліморфна реалізація перевірки місткості"""
        parent_ok = super().validate_for_request(request)
        return parent_ok and self.seats >= request.required_value

class CargoCar(Car):
    def __init__(self, id, model, condition, fuel_level, load_capacity):
        super().__init__(id, model, 'cargo', condition, fuel_level)
        self.load_capacity = load_capacity

    def validate_for_request(self, request):
        """Поліморфна реалізація перевірки вантажопідйомності"""
        parent_ok = super().validate_for_request(request)
        return parent_ok and self.load_capacity >= request.required_value