import os
import logging

from http.server import HTTPServer, BaseHTTPRequestHandler
from jinja2 import Environment, FileSystemLoader

from app.controllers.auth_controller import AuthController
from app.controllers.car_controller import CarController
from app.controllers.request_controller import RequestController
from app.controllers.driver_controller import DriverController


# Налаштовуємо базовий формат логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Створюємо об'єкт логера для цього файлу
logger = logging.getLogger(__name__)

DB_URL = "dbname=test_app user=midnight password=12345678 host=DB"
env = Environment(loader=FileSystemLoader('app/views'))

# Ініціалізуємо контролери
auth_ctrl = AuthController(env)
car_ctrl = CarController(env, DB_URL)
req_ctrl = RequestController(env, DB_URL)
driver_ctrl = DriverController(env, DB_URL)

class AutobazaHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        # 1. Відкриті маршрути (не потребують авторизації)
        if self.path == '/login':
            return auth_ctrl.render_login(self)
        if self.path == '/register':
            return auth_ctrl.render_register(self)
        if self.path == '/logout':
            return auth_ctrl.logout(self)

        # 2. Middleware аутентифікації
        if not auth_ctrl.check_auth(self):
            return

        # Дістаємо дані користувача з сесії
        user = auth_ctrl.get_current_user(self)

        # 3. Захищені маршрути
        if self.path == '/':
            req_ctrl.get_home(self)
        elif self.path == '/my_trips':
            # Перевіряємо, чи це водій
            if user and user['role'] == 'driver':
                req_ctrl.get_my_trips(self, user['id'])
            else:
                self.send_error(403, "Forbidden") # Виправили на англійську
        elif self.path == '/create_request':
            req_ctrl.render_create_form(self)
        elif self.path.startswith('/assign'):
            req_ctrl.render_assign_form(self)
        elif self.path == '/cars':
            car_ctrl.get_cars(self)
        elif self.path == '/create_car':
            car_ctrl.render_create_form(self)
        elif self.path == '/link_driver':
            if user and user['role'] == 'dispatcher':
                driver_ctrl.render_link_form(self)
            else:
                self.send_error(403, "Forbidden")
        elif self.path == '/history':
            if user and user['role'] == 'dispatcher':
                req_ctrl.get_history(self)
            else:
                self.send_error(403, "Forbidden")
        else:
            self.send_error(404, "Not Found") # Виправили на англійську

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')

        # Відкриті POST-маршрути
        if self.path == '/login':
            return auth_ctrl.login(self, post_data)
        if self.path == '/register':
            return auth_ctrl.register(self, post_data)

        # Middleware
        if not auth_ctrl.check_auth(self):
            self.send_error(403, "Forbidden")
            return

        # Отримуємо поточного користувача для перевірки ролей
        user = auth_ctrl.get_current_user(self)

        # Захищені POST-маршрути
        if self.path == '/create_request':
            req_ctrl.create_request(self, post_data)
        elif self.path == '/assign':
            req_ctrl.assign_request(self, post_data)
        elif self.path == '/create_car':
            car_ctrl.create_car(self, post_data)
        elif self.path == '/link_driver':
            driver_ctrl.create_link(self, post_data)
        elif self.path == '/complete_trip':
            if user and user['role'] == 'driver':
                req_ctrl.complete_trip(self, post_data)
            else:
                self.send_error(403, "Forbidden")
        else:
            # Виправили кирилицю, щоб не було UnicodeEncodeError!
            self.send_error(404, "Not Found")

if __name__ == "__main__":
    port = int(os.environ.get('APP_PORT', 7200))
    server = HTTPServer(('0.0.0.0', port), AutobazaHandler)
    logger.info(f"Сервер Автобази запущено на порту {port}...")
    server.serve_forever()