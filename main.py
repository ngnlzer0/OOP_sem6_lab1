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
        """Власний Routing для GET-запитів"""

        # 1. Відкриті маршрути
        if self.path == '/login':
            self.render_login()
            return

        if self.path == '/logout':
            self.send_response(302)
            self.send_header('Set-Cookie', 'session_id=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT')
            self.send_header('Location', '/login')
            self.end_headers()
            return

        # 2. Middleware аутентифікації
        user_data = self.check_auth()
        if not user_data:
            self.send_response(302)
            self.send_header('Location', '/login')
            self.end_headers()
            return

        # 3. Захищені маршрути
        if self.path == '/':
            self.render_home()
        elif self.path == '/cars':
            self.render_cars()
        elif self.path.startswith('/assign'):
            self.render_assign()
        elif self.path == '/create_request':  # <--- ДОДАНО: маршрут для сторінки створення заявки
            self.render_create_request()
        else:
            self.send_error(404, "Сторінку не знайдено")

    def do_POST(self):
        """Обробка форм через POST-запити"""
        if self.path == '/login':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')

            parsed_data = urllib.parse.parse_qs(post_data)
            login = parsed_data.get('login', [''])[0]
            password = parsed_data.get('password', [''])[0]

            if login == "admin" and password == "123":
                session_id = str(uuid.uuid4())
                SESSIONS[session_id] = {'login': login, 'role': 'dispatcher'}

                self.send_response(302)
                self.send_header('Set-Cookie', f'session_id={session_id}; Path=/; HttpOnly')
                self.send_header('Location', '/')
                self.end_headers()
            else:
                self.render_login(error="Невірний логін або пароль")

        elif self.path == '/assign':
            if not self.check_auth():
                self.send_response(403)
                self.end_headers()
                return

            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            parsed_data = urllib.parse.parse_qs(post_data)

            req_id = int(parsed_data.get('request_id', [0])[0])
            car_id = int(parsed_data.get('car_id', [0])[0])
            driver_id = int(parsed_data.get('driver_id', [0])[0])

            print(f"Створюємо рейс: Заявка={req_id}, Авто={car_id}, Водій={driver_id}")

            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()

        elif self.path == '/create_request':  # <--- ДОДАНО: логіка збереження нової заявки в БД
            if not self.check_auth():
                self.send_response(403)
                self.end_headers()
                return

            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            parsed_data = urllib.parse.parse_qs(post_data)

            destination = parsed_data.get('destination', [''])[0]
            req_type = parsed_data.get('required_type', [''])[0]
            req_value = float(parsed_data.get('required_value', [0])[0])

            try:
                dao = RequestDAO(DB_URL)
                dao.create_request(req_type, req_value, destination)
            except Exception as e:
                print(f"Помилка створення заявки: {e}")

            # Після успішного створення перекидаємо на головну сторінку
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()

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

    def render_assign(self):
        try:
            query_components = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            req_id = int(query_components.get('req_id', [0])[0])

            if not req_id:
                self.send_error(400, "Bad Request: відсутній req_id")
                return

            req_dao = RequestDAO(DB_URL)
            car_dao = CarDAO(DB_URL)

            all_reqs = req_dao.get_all_pending()
            current_request = next((r for r in all_reqs if r.id == req_id), None)

            if not current_request:
                self.send_error(404, "Заявку не знайдено")
                return

            all_cars = car_dao.get_all()
            valid_cars = [car for car in all_cars if car.validate_for_request(current_request)]

            template = env.get_template('assign.html')
            output = template.render(request=current_request, valid_cars=valid_cars)

            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(output.encode('utf-8'))
        except Exception as e:
            self.send_error(500, f"Помилка сервера: {e}")

    # <--- ДОДАНО: Метод для відображення сторінки з формою створення
    def render_create_request(self):
        try:
            template = env.get_template('create_request.html')
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(template.render().encode('utf-8'))
        except Exception as e:
            self.send_error(500, f"Помилка сервера: {e}")


if __name__ == "__main__":
    server = HTTPServer(('0.0.0.0', 7200), AutobazaHandler)
    print("Сервер Автобази запущено на порту 7200...")
    server.serve_forever()