import uuid
import urllib.parse
from http.cookies import SimpleCookie
from app.DAO.user_dao import UserDAO
import uuid
import urllib.parse


class AuthController:
    def __init__(self, template_env):
        self.env = template_env
        self.sessions = {}  # Інкапсулюємо сховище сесій тут

    def check_auth(self, handler):
        """Перевіряє, чи авторизований користувач. Якщо ні - робить редирект і повертає False."""
        cookie_header = handler.headers.get('Cookie')
        if cookie_header:
            cookie = SimpleCookie(cookie_header)
            if 'session_id' in cookie:
                session_id = cookie['session_id'].value
                if session_id in self.sessions:
                    return True

        # Якщо сесії немає - редирект
        handler.send_response(302)
        handler.send_header('Location', '/login')
        handler.end_headers()
        return False

    def render_login(self, handler, error=None):
        template = self.env.get_template('login.html')
        handler.send_response(200)
        handler.send_header("Content-type", "text/html; charset=utf-8")
        handler.end_headers()
        handler.wfile.write(template.render(error=error).encode('utf-8'))

    def login(self, handler, post_data):

        # Беремо URL бази даних з контролера (або можна передавати з main.py)
        # Для простоти поки захардкодимо підключення тут, або використай константу
        db_url = "dbname=test_app user=midnight password=12345678 host=DB"

        parsed_data = urllib.parse.parse_qs(post_data)
        login = parsed_data.get('login', [''])[0]
        password = parsed_data.get('password', [''])[0]

        # 1. Звертаємося до бази даних
        user_dao = UserDAO(db_url)
        user_data = user_dao.authenticate(login, password)

        # 2. Якщо користувача знайдено
        if user_data:
            session_id = str(uuid.uuid4())
            # Записуємо в сесію всю важливу інфу, включаючи роль
            self.sessions[session_id] = {
                'id': user_data['id'],
                'login': user_data['login'],
                'role': user_data['role']
            }

            handler.send_response(302)
            handler.send_header('Set-Cookie', f'session_id={session_id}; Path=/; HttpOnly')

            # 3. РОЗПОДІЛ РОЛЕЙ: Водіїв кидаємо в їхній кабінет, диспетчерів - на головну
            if user_data['role'] == 'driver':
                handler.send_header('Location', '/my_trips')
            else:
                handler.send_header('Location', '/')

            handler.end_headers()
        else:
            # Якщо логін/пароль неправильні
            self.render_login(handler, error="Невірний логін або пароль")

    def logout(self, handler):
        handler.send_response(302)
        handler.send_header('Set-Cookie', 'session_id=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT')
        handler.send_header('Location', '/login')
        handler.end_headers()

    def render_register(self, handler, error=None):
        template = self.env.get_template('register.html')
        handler.send_response(200)
        handler.send_header("Content-type", "text/html; charset=utf-8")
        handler.end_headers()
        handler.wfile.write(template.render(error=error).encode('utf-8'))

    def register(self, handler, post_data):

        db_url = "dbname=test_app user=midnight password=12345678 host=DB"

        parsed_data = urllib.parse.parse_qs(post_data)
        login = parsed_data.get('login', [''])[0]
        password = parsed_data.get('password', [''])[0]
        role = parsed_data.get('role', ['dispatcher'])[0]

        user_dao = UserDAO(db_url)
        new_user_id = user_dao.create_user(login, password, role)

        if new_user_id:
            # Якщо реєстрація успішна - перенаправляємо на сторінку входу
            handler.send_response(302)
            handler.send_header('Location', '/login')
            handler.end_headers()
        else:
            # Якщо логін вже зайнятий
            self.render_register(handler, error="Цей логін вже зайнятий. Виберіть інший.")

        # Додай цей метод всередину класу AuthController
        def get_current_user(self, handler):
            """Повертає дані поточного користувача із сесії"""
            from http.cookies import SimpleCookie
            cookie_header = handler.headers.get('Cookie')
            if cookie_header:
                cookie = SimpleCookie(cookie_header)
                if 'session_id' in cookie:
                    session_id = cookie['session_id'].value
                    return self.sessions.get(session_id)
            return None