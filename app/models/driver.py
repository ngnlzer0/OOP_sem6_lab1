class Driver:
    def __init__(self, id, user_id, car_id, passport):
        self.id = id
        self.user_id = user_id
        self.car_id = car_id
        self.active_trip = None