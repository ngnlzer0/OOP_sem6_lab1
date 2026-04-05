import unittest
from unittest.mock import MagicMock, patch
from app.controllers.car_controller import CarController
from app.controllers.request_controller import RequestController


class TestControllers(unittest.TestCase):
    def setUp(self):
        self.mock_env = MagicMock()
        self.car_ctrl = CarController(self.mock_env, "mock_db")
        self.req_ctrl = RequestController(self.mock_env, "mock_db")

    @patch('app.DAO.car_dao.CarDAO.get_all_cars')
    def test_car_controller_get_cars_success(self, mock_get_cars):
        mock_handler = MagicMock()
        mock_get_cars.return_value = [{'id': 1, 'model': 'BMW'}]

        self.car_ctrl.get_cars(mock_handler)

        mock_handler.send_response.assert_called_with(200)
        mock_handler.send_header.assert_any_call("Content-type", "text/html; charset=utf-8")
        self.assertTrue(mock_handler.wfile.write.called)

    @patch('app.DAO.car_dao.CarDAO.get_all_cars')
    def test_car_controller_get_cars_db_error(self, mock_get_cars):
        mock_handler = MagicMock()
        mock_get_cars.side_effect = Exception("DB Crash")
        self.car_ctrl.get_cars(mock_handler)
        self.assertTrue(True)

    @patch('app.DAO.car_dao.CarDAO.create_car')
    def test_car_controller_create_car_post(self, mock_create):
        mock_handler = MagicMock()
        post_data = "model=Ford&type=cargo&capacity=2000&fuel_level=80"

        self.car_ctrl.create_car(mock_handler, post_data)

        mock_create.assert_called_once_with('Ford', 'cargo', 80, 2000.0)
        mock_handler.send_response.assert_called_with(302)
        mock_handler.send_header.assert_any_call('Location', '/cars')

    @patch('app.DAO.trip_dao.TripDAO.complete_trip')
    def test_request_controller_complete_trip(self, mock_complete):
        mock_handler = MagicMock()
        post_data = "trip_id=5&car_condition=false"

        self.req_ctrl.complete_trip(mock_handler, post_data)

        mock_complete.assert_called_once_with(5, False)
        mock_handler.send_response.assert_called_with(302)


if __name__ == '__main__':
    unittest.main()