import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from backend.app.routes.route_user_management import RegisterUser, LoginUser

class UserManagementTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.add_url_rule('/register', view_func=RegisterUser.as_view('register'))
        self.app.add_url_rule('/login', view_func=LoginUser.as_view('login'))
        self.client = self.app.test_client()

    @patch('backend.app.routes.route_user_management.collection.insert_one')
    def test_user_registered_successfully(self, mock_insert):
        mock_insert.return_value = MagicMock()
        response = self.client.post('/register', headers={'Username': 'testuser', 'Password': 'testpass'})
        self.assertEqual(200, response.status_code)
        self.assertIn('User registered successfully', response.data.decode())

    @patch('backend.app.routes.route_user_management.collection.find_one')
    def test_username_already_exists(self, mock_find):
        mock_find.return_value = {'Username': 'testuser'}
        response = self.client.post('/register', headers={'Username': 'testuser', 'Password': 'testpass'})
        self.assertEqual(409, response.status_code)
        self.assertIn('Username already exists', response.data.decode())

    @patch('backend.app.routes.route_user_management.collection.insert_one')
    def test_registration_error(self, mock_insert):
        mock_insert.side_effect = Exception('Database error')
        response = self.client.post('/register', headers={'Username': 'testuser', 'Password': 'testpass'})
        self.assertEqual(500, response.status_code)
        self.assertIn('Error occurred: Database error', response.data.decode())

    @patch('backend.app.routes.route_user_management.collection.find_one')
    @patch('backend.app.routes.route_user_management.ph', new_callable=MagicMock)
    def test_user_logged_in_successfully(self, mock_ph, mock_find):
        mock_find.return_value = {'Username': 'testuser', 'Password': 'hashedpassword'}
        mock_ph.verify.return_value = True  # Simuliere erfolgreiche Passwortverifizierung

        response = self.client.post('/login', headers={'Username': 'testuser', 'Password': 'testpass'})

        self.assertEqual(200, response.status_code)
        self.assertIn('User logged in successfully', response.data.decode())

    @patch('backend.app.routes.route_user_management.collection.find_one')
    def test_invalid_login_credentials(self, mock_find):
        mock_find.return_value = None
        response = self.client.post('/login', headers={'Username': 'testuser', 'Password': 'testpass'})
        self.assertEqual(401, response.status_code)
        self.assertIn('Invalid username or password', 'Invalid username or password')

    @patch('backend.app.routes.route_user_management.collection.find_one')
    def test_login_error(self, mock_find):
        mock_find.side_effect = Exception('Database error')
        response = self.client.post('/login', headers={'Username': 'testuser', 'Password': 'testpass'})
        self.assertEqual(500, response.status_code)
        self.assertIn('Error occurred: Database error', response.data.decode())
