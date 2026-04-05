class Request:
    def __init__(self, request_id, required_type, required_value, destination, status='pending'):
        # Інкапсуляція даних заявки
        self.id = request_id
        self.required_type = required_type
        self.required_value = required_value
        self.destination = destination
        self.status = status