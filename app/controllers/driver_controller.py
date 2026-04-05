import urllib.parse
from app.DAO.driver_dao import DriverDAO
import logging

logger = logging.getLogger(__name__)


class DriverController:
    def __init__(self, template_env, db_url):
        self.env = template_env
        self.db_url = db_url

    def render_link_form(self, handler):
        try:
            dao = DriverDAO(self.db_url)
            # Дістаємо списки для випадаючих меню у формі
            users = dao.get_unassigned_users()
            cars = dao.get_available_cars()

            template = self.env.get_template('link_driver.html')

            handler.send_response(200)
            handler.send_header("Content-type", "text/html; charset=utf-8")
            handler.end_headers()
            handler.wfile.write(template.render(users=users, cars=cars).encode('utf-8'))
        except Exception as e:
            handler.send_error(500, f"Помилка БД: {e}")

    def create_link(self, handler, post_data):
        parsed_data = urllib.parse.parse_qs(post_data)
        user_id = int(parsed_data.get('user_id', [0])[0])
        car_id = int(parsed_data.get('car_id', [0])[0])
        passport = parsed_data.get('passport', [''])[0]

        try:
            dao = DriverDAO(self.db_url)
            dao.link_driver(user_id, car_id, passport)
        except Exception as e:
            logger.error(f"Помилка закріплення водія: {e}")

        # Повертаємо на головну
        handler.send_response(302)
        handler.send_header('Location', '/')
        handler.end_headers()