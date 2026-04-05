from app.DAO.car_dao import CarDAO
import urllib.parse


class CarController:
    def __init__(self, template_env, db_url):
        self.env = template_env
        self.db_url = db_url

    def get_cars(self, handler):
        from app.DAO.car_dao import CarDAO
        try:
            dao = CarDAO(self.db_url)
            # Викликаємо оновлений метод
            cars = dao.get_all_cars()
            template = self.env.get_template('cars.html')

            handler.send_response(200)
            handler.send_header("Content-type", "text/html; charset=utf-8")
            handler.end_headers()
            # Додаємо user_role, щоб навігація диспетчера працювала
            handler.wfile.write(template.render(cars=cars, user_role='dispatcher').encode('utf-8'))
        except Exception as e:
            handler.send_error(500, f"Помилка БД: {e}")

    def render_create_form(self, handler):
        template = self.env.get_template('create_car.html')
        handler.send_response(200)
        handler.send_header("Content-type", "text/html; charset=utf-8")
        handler.end_headers()
        handler.wfile.write(template.render().encode('utf-8'))

    def create_car(self, handler, post_data):
        import urllib.parse
        from app.DAO.car_dao import CarDAO

        parsed_data = urllib.parse.parse_qs(post_data)
        model = parsed_data.get('model', [''])[0]
        car_type = parsed_data.get('type', ['passenger'])[0]
        capacity = float(parsed_data.get('capacity', [0])[0])
        fuel_level = int(parsed_data.get('fuel_level', [100])[0])

        try:
            dao = CarDAO(self.db_url)
            dao.create_car(model, car_type, fuel_level, capacity)
        except Exception as e:
            print(f"Помилка створення авто: {e}")

        # Після додавання перекидаємо назад в автопарк
        handler.send_response(302)
        handler.send_header('Location', '/cars')
        handler.end_headers()