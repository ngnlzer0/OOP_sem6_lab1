class Trip:
    def complete(self, end_condition):
        """Метод для відмітки про виконання рейсу"""
        self.is_completed = True
        self.end_condition = end_condition
