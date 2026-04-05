# app/controllers/request_controller.py
import urllib.parse
from app.DAO.request_dao import RequestDAO
from app.DAO.car_dao import CarDAO


class RequestController:
    def __init__(self, template_env, db_url):
        self.env = template_env
        self.db_url = db_url

    def get_home(self, handler):
        try:
            dao = RequestDAO(self.db_url)
            pending_requests = dao.get_all_pending()
            template = self.env.get_template('index.html')

            handler.send_response(200)
            handler.send_header("Content-type", "text/html; charset=utf-8")
            handler.end_headers()
            handler.wfile.write(template.render(requests=pending_requests).encode('utf-8'))
        except Exception as e:
            handler.send_error(500, f"Помилка БД: {e}")

    def render_create_form(self, handler):
        template = self.env.get_template('create_request.html')
        handler.send_response(200)
        handler.send_header("Content-type", "text/html; charset=utf-8")
        handler.end_headers()
        handler.wfile.write(template.render().encode('utf-8'))

    def create_request(self, handler, post_data):
        parsed_data = urllib.parse.parse_qs(post_data)
        destination = parsed_data.get('destination', [''])[0]
        req_type = parsed_data.get('required_type', [''])[0]
        req_value = float(parsed_data.get('required_value', [0])[0])

        dao = RequestDAO(self.db_url)
        dao.create_request(req_type, req_value, destination)

        handler.send_response(302)
        handler.send_header('Location', '/')
        handler.end_headers()

    def render_assign_form(self, handler):
        try:
            query_components = urllib.parse.parse_qs(urllib.parse.urlparse(handler.path).query)
            req_id = int(query_components.get('req_id', [0])[0])

            req_dao = RequestDAO(self.db_url)
            car_dao = CarDAO(self.db_url)

            all_reqs = req_dao.get_all_pending()
            current_request = next((r for r in all_reqs if r.id == req_id), None)

            if not current_request:
                handler.send_error(404, "Заявку не знайдено")
                return

            all_cars = car_dao.get_all()
            valid_cars = [car for car in all_cars if car.validate_for_request(current_request)]

            template = self.env.get_template('assign.html')

            handler.send_response(200)
            handler.send_header("Content-type", "text/html; charset=utf-8")
            handler.end_headers()
            handler.wfile.write(template.render(request=current_request, valid_cars=valid_cars).encode('utf-8'))
        except Exception as e:
            handler.send_error(500, f"Помилка: {e}")

    def assign_request(self, handler, post_data):
        import urllib.parse
        from app.DAO.trip_dao import TripDAO
        from app.DAO.request_dao import RequestDAO

        parsed_data = urllib.parse.parse_qs(post_data)
        req_id = int(parsed_data.get('request_id', [0])[0])
        car_id = int(parsed_data.get('car_id', [0])[0])

        try:
            # 1. Створюємо рейс (автоматично підтягне водія)
            trip_dao = TripDAO(self.db_url)
            trip_dao.create_trip_by_car(req_id, car_id)

            # 2. Змінюємо статус заявки, щоб вона не висіла як 'pending'
            req_dao = RequestDAO(self.db_url)
            req_dao.update_status(req_id, 'assigned')
        except Exception as e:
            print(f"Помилка створення рейсу: {e}")

        # Повертаємо диспетчера на головну сторінку
        handler.send_response(302)
        handler.send_header('Location', '/')
        handler.end_headers()

    def get_my_trips(self, handler, user_id):
        from app.DAO.trip_dao import TripDAO
        try:
            dao = TripDAO(self.db_url)
            trips = dao.get_driver_trips(user_id)
            template = self.env.get_template('my_trips.html')

            handler.send_response(200)
            handler.send_header("Content-type", "text/html; charset=utf-8")
            handler.end_headers()
            handler.wfile.write(template.render(trips=trips).encode('utf-8'))
        except Exception as e:
            handler.send_error(500, f"Помилка БД: {e}")