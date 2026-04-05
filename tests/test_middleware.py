import unittest
from unittest.mock import MagicMock
from app.controllers.auth_controller import AuthController

class TestAuthMiddleware(unittest.TestCase):
    def setUp(self):
        self.auth_ctrl = AuthController(MagicMock())
        self.auth_ctrl.sessions["valid_sid"] = {"id": 1, "role": "dispatcher"}

    def test_check_auth_no_cookie_redirects_to_login(self):
        handler = MagicMock()
        handler.headers.get.return_value = None
        result = self.auth_ctrl.check_auth(handler)
        self.assertFalse(result)
        handler.send_response.assert_called_with(302)
        handler.send_header.assert_called_with('Location', '/login')

    def test_check_auth_invalid_cookie_redirects(self):
        handler = MagicMock()
        handler.headers.get.return_value = "session_id=hacker_sid"
        result = self.auth_ctrl.check_auth(handler)
        self.assertFalse(result)
        handler.send_response.assert_called_with(302)

    def test_check_auth_valid_cookie_allows_access(self):
        handler = MagicMock()
        handler.headers.get.return_value = "session_id=valid_sid"
        result = self.auth_ctrl.check_auth(handler)
        self.assertTrue(result)
        handler.send_response.assert_not_called()

    def test_get_current_user_success(self):
        handler = MagicMock()
        handler.headers.get.return_value = "session_id=valid_sid"
        user = self.auth_ctrl.get_current_user(handler)
        self.assertEqual(user["role"], "dispatcher")

    def test_logout_destroys_session(self):
        handler = MagicMock()
        handler.headers.get.return_value = "session_id=valid_sid"
        self.auth_ctrl.logout(handler)
        handler.send_response.assert_called_with(302)

if __name__ == '__main__':
    unittest.main()