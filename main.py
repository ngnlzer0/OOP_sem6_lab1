import os
import urllib.parse
import uuid
from http.server import HTTPServer, BaseHTTPRequestHandler
from http.cookies import SimpleCookie
from jinja2 import Environment, FileSystemLoader

# Імпорти моделей та DAO
from app.DAO.request_dao import RequestDAO
from app.DAO.car_dao import CarDAO

# from app.dao.user_dao import UserDAO # Розкоментуємо, коли створимо

DB_URL = "dbname=test_app user=midnight password=12345678 host=DB"

# Ініціалізація Jinja2 (Вимога №22)
env = Environment(loader=FileSystemLoader('app/views'))

# Сховище сесій у пам'яті сервера (Вимога №24)
SESSIONS = {}


class AutobazaHandler(BaseHTTPRequestHandler):

    def check_auth(self):
        """Перевірка наявності та валідності Cookie"""
        cookie_header = self.headers.get('Cookie')
        if cookie_header:
            cookie = SimpleCookie(cookie_header)
            if 'session_id' in cookie:
                session_id = cookie['session_id'].value
                if session_id in SESSIONS:
                    return SESSIONS[session_id]
        return None

    def do_GET(self):
        """Власний Routing для GET-запитів (Вимога №15)"""

        # 1. Відкриті маршрути
        if self.path == '/login':
            self.render_login()
            return

        if self.path == '/logout':
            self.send_response(302)
            # Встановлюємо Cookie з минулою датою, щоб браузер її видалив
            self.send_header('Set-Cookie', 'session_id=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT')
            self.send_header('Location', '/login')
            self.end_headers()
            return

        # 2. Middleware аутентифікації
        user_data = self.check_auth()
        if not user_data:
            # Якщо користувач не авторизований - редирект на вхід [cite: 24, 34, 44, 54, 65, 75, 85]
            self.send_response(302)
            self.send_header('Location', '/login')
            self.end_headers()
            return

        # 3. Захищені маршрути
        if self.path == '/':
            self.render_home()
        elif self.path == '/cars':
            self.render_cars()
        else:
            self.send_error(404, "Сторінку не знайдено")

    def do_POST(self):
        """Обробка форм через POST-запити (Вимога №12)"""
        if self.path == '/login':
            # Читаємо тіло запиту (дані з форми)
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')

            # Парсимо дані (напр. "login=admin&password=123")
            parsed_data = urllib.parse.parse_qs(post_data)
            login = parsed_data.get('login', [''])[0]
            password = parsed_data.get('password', [''])[0]

            # TODO: Замінити hardcode на виклик UserDAO
            if login == "admin" and password == "123":
                # Генеруємо унікальний session_id
                session_id = str(uuid.uuid4())
                SESSIONS[session_id] = {'login': login, 'role': 'dispatcher'}

                # Встановлюємо Cookie та робимо редирект
                self.send_response(302)
                self.send_header('Set-Cookie', f'session_id={session_id}; Path=/; HttpOnly')
                self.send_header('Location', '/')
                self.end_headers()
            else:
                self.render_login(error="Невірний логін або пароль")
        else:
            self.send_error(404, "Сторінку не знайдено")

    # --- CONTROLLERS (Відповідь + View) ---

    def render_login(self, error=None):
        template = env.get_template('login.html')
        output = template.render(error=error)

        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(output.encode('utf-8'))

    def render_home(self):
        try:
            dao = RequestDAO(DB_URL)
            pending_requests = dao.get_all_pending()
            template = env.get_template('index.html')
            output = template.render(requests=pending_requests)

            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(output.encode('utf-8'))
        except Exception as e:
            self.send_error(500, f"Помилка БД: {e}")

    def render_cars(self):
        try:
            dao = CarDAO(DB_URL)
            all_cars = dao.get_all()
            template = env.get_template('cars.html')
            output = template.render(cars=all_cars)

            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(output.encode('utf-8'))
        except Exception as e:
            self.send_error(500, f"Помилка БД: {e}")


if __name__ == "__main__":
    server = HTTPServer(('0.0.0.0', 7200), AutobazaHandler)
    print("Сервер Автобази запущено на порту 7200...")
    server.serve_forever()