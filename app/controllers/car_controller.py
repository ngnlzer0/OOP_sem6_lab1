from app.DAO.car_dao import CarDAO
import urllib.parse


class CarController:
    def __init__(self, template_env, db_url):
        self.env = template_env
        self.db_url = db_url

    def get_cars(self, handler):
        """Обробка GET /cars"""
        try:
            dao = CarDAO(self.db_url)
            all_cars = dao.get_all()
            template = self.env.get_template('cars.html')
            output = template.render(cars=all_cars)

            handler.send_response(200)
            handler.send_header("Content-type", "text/html; charset=utf-8")
            handler.end_headers()
            handler.wfile.write(output.encode('utf-8'))
        except Exception as e:
            handler.send_error(500, f"Помилка БД: {e}")

    def render_create_form(self, handler):
        """Обробка GET /create_car"""
        template = self.env.get_template('create_car.html')
        handler.send_response(200)
        handler.send_header("Content-type", "text/html; charset=utf-8")
        handler.end_headers()
        handler.wfile.write(template.render().encode('utf-8'))

    def create_car(self, handler, post_data):
        """Обробка POST /create_car"""
        parsed_data = urllib.parse.parse_qs(post_data)

        model = parsed_data.get('model', [''])[0]
        car_type = parsed_data.get('car_type', [''])[0]
        capacity = int(parsed_data.get('capacity', [0])[0])
        fuel_level = int(parsed_data.get('fuel_level', [100])[0])
        condition = parsed_data.get('condition', ['True'])[0] == 'True'

        dao = CarDAO(self.db_url)
        dao.create_car(model, car_type, condition, fuel_level, capacity)

        handler.send_response(302)
        handler.send_header('Location', '/cars')
        handler.end_headers()