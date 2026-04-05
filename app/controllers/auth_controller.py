import uuid
import urllib.parse
from http.cookies import SimpleCookie


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
        parsed_data = urllib.parse.parse_qs(post_data)
        login = parsed_data.get('login', [''])[0]
        password = parsed_data.get('password', [''])[0]

        # TODO: Замінити на виклик UserDAO
        if login == "admin" and password == "123":
            session_id = str(uuid.uuid4())
            self.sessions[session_id] = {'login': login, 'role': 'dispatcher'}

            handler.send_response(302)
            handler.send_header('Set-Cookie', f'session_id={session_id}; Path=/; HttpOnly')
            handler.send_header('Location', '/')
            handler.end_headers()
        else:
            self.render_login(handler, error="Невірний логін або пароль")

    def logout(self, handler):
        handler.send_response(302)
        handler.send_header('Set-Cookie', 'session_id=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT')
        handler.send_header('Location', '/login')
        handler.end_headers()