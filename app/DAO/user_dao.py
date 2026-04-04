# app/dao/user_dao.py
from app.DAO.base_dao import BaseDAO
from app.models.user import User

class UserDAO(BaseDAO):
    def get_by_login(self, login):
        query = "SELECT id, login, password_hash, role FROM users WHERE login = %s"
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (login,))
                row = cur.fetchone()
                if row:
                    return User(*row)
        return None