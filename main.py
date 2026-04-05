import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from jinja2 import Environment, FileSystemLoader

from app.controllers.auth_controller import AuthController
from app.controllers.car_controller import CarController
from app.controllers.request_controller import RequestController

DB_URL = "dbname=test_app user=midnight password=12345678 host=DB"
env = Environment(loader=FileSystemLoader('app/views'))

# Ініціалізуємо контролери
auth_ctrl = AuthController(env)
car_ctrl = CarController(env, DB_URL)
req_ctrl = RequestController(env, DB_URL)

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
        # Якщо check_auth повертає False (сесії немає), метод завершується (return)
        if not auth_ctrl.check_auth(self):
            return

        # 3. Захищені маршрути
        if self.path == '/':
            req_ctrl.get_home(self)
        elif self.path == '/create_request':
            req_ctrl.render_create_form(self)
        elif self.path.startswith('/assign'):
            req_ctrl.render_assign_form(self)
        elif self.path == '/cars':
            car_ctrl.get_cars(self)
        elif self.path == '/create_car':
            car_ctrl.render_create_form(self)
        else:
            self.send_error(404, "Сторінку не знайдено")

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')

        # Відкритий POST-маршрут
        # Відкриті POST-маршрути
        if self.path == '/login':
            return auth_ctrl.login(self, post_data)
        if self.path == '/register':
            return auth_ctrl.register(self, post_data)
        # Middleware
        if not auth_ctrl.check_auth(self):
            self.send_response(403)
            self.end_headers()
            return

        # Захищені POST-маршрути
        if self.path == '/create_request':
            req_ctrl.create_request(self, post_data)
        elif self.path == '/assign':
            req_ctrl.assign_request(self, post_data)
        elif self.path == '/create_car':
            car_ctrl.create_car(self, post_data)
        else:
            self.send_error(404, "Сторінку не знайдено")

if __name__ == "__main__":
    port = int(os.environ.get('APP_PORT', 7200))
    server = HTTPServer(('0.0.0.0', port), AutobazaHandler)
    print(f"Сервер Автобази запущено на порту {port}...")
    server.serve_forever()