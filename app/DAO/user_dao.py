# app/dao/user_dao.py
import psycopg2


class UserDAO:
    def __init__(self, db_url):
        self.db_url = db_url

    def get_connection(self):
        return psycopg2.connect(self.db_url)

    def authenticate(self, login, password):
        """
        Перевіряє користувача в базі даних.
        Повертає словник з даними (id, login, role) або None.
        """
        # Зверни увагу: слово "user" в лапках, бо це зарезервоване слово в SQL
        query = 'SELECT id, login, role FROM "user" WHERE login = %s AND password_hash = %s'

        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (login, password))
                user_record = cur.fetchone()

                if user_record:
                    return {
                        'id': user_record[0],
                        'login': user_record[1],
                        'role': user_record[2]
                    }
                return None

    def create_user(self, login, password, role):
        """
        Створює нового користувача.
        Повертає ID користувача, або None, якщо такий логін вже існує.
        """
        query = 'INSERT INTO "user" (login, password_hash, role) VALUES (%s, %s, %s) RETURNING id'

        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (login, password, role))
                    new_id = cur.fetchone()[0]
                    conn.commit()
                    return new_id
        except psycopg2.IntegrityError:
            # Спрацює, якщо логін не унікальний (порушення UNIQUE constraint)
            return None