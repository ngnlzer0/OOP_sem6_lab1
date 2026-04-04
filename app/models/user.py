# app/models/user.py
class User:
    def __init__(self, user_id, login, password_hash, role):
        self.id = user_id
        self.login = login
        self.password_hash = password_hash
        self.role = role # 'dispatcher' або 'driver'