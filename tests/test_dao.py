import unittest
from unittest.mock import MagicMock, patch
from app.DAO.request_dao import RequestDAO
from app.DAO.car_dao import CarDAO


class TestDAO(unittest.TestCase):
    def setUp(self):
        self.db_url = "mock_url"
        self.req_dao = RequestDAO(self.db_url)
        self.car_dao = CarDAO(self.db_url)

    @patch('psycopg.connect')
    def test_request_dao_update_status(self, mock_connect):
        mock_conn = mock_connect.return_value.__enter__.return_value
        mock_cur = mock_conn.cursor.return_value.__enter__.return_value

        self.req_dao.update_status(10, 'assigned')

        expected_query = "UPDATE request SET status = %s WHERE id = %s"
        mock_cur.execute.assert_called_once_with(expected_query, ('assigned', 10))
        self.assertTrue(mock_conn.commit.called)

    @patch('psycopg.connect')
    def test_car_dao_get_cars_for_assignment(self, mock_connect):
        mock_conn = mock_connect.return_value.__enter__.return_value
        mock_cur = mock_conn.cursor.return_value.__enter__.return_value
        mock_cur.fetchall.return_value = [(1, "Sprinter", "Ivan")]

        cars = self.car_dao.get_cars_for_assignment('passenger', 15)

        self.assertEqual(len(cars), 1)
        self.assertEqual(cars[0]['driver_name'], "Ivan")
        self.assertTrue(mock_cur.execute.called)


if __name__ == '__main__':
    unittest.main()