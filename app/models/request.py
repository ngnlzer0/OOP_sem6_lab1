class Request:
    def __init__(self, request_id, required_type, required_value, destination, status='pending'):
        # Інкапсуляція даних заявки
        self.id = request_id
        self.required_type = required_type  # 'passenger' або 'cargo' [cite: 106]
        self.required_value = required_value  # Кількість місць або вага [cite: 106]
        self.destination = destination
        self.status = status