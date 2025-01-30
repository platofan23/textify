import logging
import unittest
from unittest.mock import patch, MagicMock, mock_open
from flask import Flask

from backend.app.routes import RegisterUser, LoginUser

# Configure logging to capture DEBUG-level messages and above.
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class UserManagementTestCase(unittest.TestCase):
    def setUp(self):
        """
        Set up the Flask test application and initialize test client.
        Add routes for user registration and login.
        """
        logger.debug("Setting up the Flask test application and routes.")
        self.app = Flask(__name__)
        self.app.add_url_rule('/register', view_func=RegisterUser.as_view('register'))
        self.app.add_url_rule('/login', view_func=LoginUser.as_view('login'))
        self.client = self.app.test_client()
        logger.debug("Flask test client initialized.")

    @patch('backend.app.routes.route_user_management.collection.insert_one')
    @patch('builtins.open', new_callable=mock_open, read_data='[]')
    def test_user_registered_successfully(self, mock_file, mock_insert):
        """
        Test that a user is registered successfully when valid details are provided.
        """
        logger.debug("Starting test: test_user_registered_successfully.")
        # Simulate a successful database insertion.
        mock_insert.return_value = MagicMock()
        # Send a POST request to the /register endpoint.
        response = self.client.post('/register', headers={'Username': 'testuser', 'Password': 'testpass'})
        logger.debug("Received response: status_code=%s, data=%s", response.status_code, response.data.decode())
        # Assert that the response indicates success.
        self.assertEqual(200, response.status_code)
        self.assertIn('User registered successfully', response.data.decode())
        logger.debug("test_user_registered_successfully passed.")

    @patch('backend.app.routes.route_user_management.collection.find_one')
    def test_username_already_exists(self, mock_find):
        """
        Test that attempting to register an already existing username returns a conflict error.
        """
        logger.debug("Starting test: test_username_already_exists.")
        # Simulate finding an existing user in the database.
        mock_find.return_value = {'Username': 'testuser'}
        # Send a POST request to the /register endpoint.
        response = self.client.post('/register', headers={'Username': 'testuser', 'Password': 'testpass'})
        logger.debug("Received response: status_code=%s, data=%s", response.status_code, response.data.decode())
        # Assert that the response indicates a conflict (username already exists).
        self.assertEqual(409, response.status_code)
        self.assertIn('Username already exists', response.data.decode())
        logger.debug("test_username_already_exists passed.")

    @patch('backend.app.routes.route_user_management.collection.insert_one')
    @patch('builtins.open', new_callable=mock_open, read_data='[]')
    def test_registration_error(self, mock_file, mock_insert):
        """
        Test that a server error during registration is handled correctly.
        """
        logger.debug("Starting test: test_registration_error.")
        # Simulate a database error during user registration.
        mock_insert.side_effect = Exception('Database error')
        # Send a POST request to the /register endpoint.
        response = self.client.post('/register', headers={'Username': 'testuser', 'Password': 'testpass'})
        logger.debug("Received response: status_code=%s, data=%s", response.status_code, response.data.decode())
        # Assert that the response indicates an internal server error.
        self.assertEqual(500, response.status_code)
        self.assertIn('Error occurred: Database error', response.data.decode())
        logger.debug("test_registration_error passed.")

    @patch('backend.app.routes.route_user_management.collection.find_one')
    @patch('backend.app.routes.route_user_management.ph', new_callable=MagicMock)
    def test_user_logged_in_successfully(self, mock_ph, mock_find):
        """
        Test that a user is logged in successfully with valid credentials.
        """
        logger.debug("Starting test: test_user_logged_in_successfully.")
        # Simulate finding a user in the database and successful password verification.
        mock_find.return_value = {'Username': 'testuser', 'Password': 'hashedpassword'}
        mock_ph.verify.return_value = True
        # Send a POST request to the /login endpoint.
        response = self.client.post('/login', headers={'Username': 'testuser', 'Password': 'testpass'})
        logger.debug("Received response: status_code=%s, data=%s", response.status_code, response.data.decode())
        # Assert that the response indicates success.
        self.assertEqual(200, response.status_code)
        self.assertIn('User logged in successfully', response.data.decode())
        logger.debug("test_user_logged_in_successfully passed.")

    @patch('backend.app.routes.route_user_management.collection.find_one')
    def test_invalid_login_credentials(self, mock_find):
        """
        Test that invalid login credentials result in an unauthorized response.
        """
        logger.debug("Starting test: test_invalid_login_credentials.")
        # Simulate that no matching user is found in the database.
        mock_find.return_value = None
        # Send a POST request to the /login endpoint.
        response = self.client.post('/login', headers={'Username': 'testuser', 'Password': 'testpass'})
        logger.debug("Received response: status_code=%s, data=%s", response.status_code, response.data.decode())
        # Assert that the response indicates unauthorized access.
        self.assertEqual(401, response.status_code)
        self.assertIn('Username or password not found', response.data.decode())
        logger.debug("test_invalid_login_credentials passed.")

    @patch('backend.app.routes.route_user_management.collection.find_one')
    def test_login_error(self, mock_find):
        """
        Test that a server error during login is handled correctly.
        """
        logger.debug("Starting test: test_login_error.")
        # Simulate a database error during user login.
        mock_find.side_effect = Exception('Database error')
        # Send a POST request to the /login endpoint.
        response = self.client.post('/login', headers={'Username': 'testuser', 'Password': 'testpass'})
        logger.debug("Received response: status_code=%s, data=%s", response.status_code, response.data.decode())
        # Assert that the response indicates an internal server error.
        self.assertEqual(500, response.status_code)
        self.assertIn('Error occurred: Database error', response.data.decode())
        logger.debug("test_login_error passed.")


if __name__ == '__main__':
    unittest.main()