import hashlib
import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from backend.app.routes.user_management import user_management_bp

class UserManagementTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(user_management_bp)
        self.client = self.app.test_client()

    @patch('backend.app.routes.user_management.collection.insert_one')
    def test_user_registered_successfully(self, mock_insert):
        mock_insert.return_value = MagicMock()
        response = self.client.post('/register', headers={'Username': 'testuser', 'Password': 'testpass'})
        self.assertEqual(200, response.status_code)
        self.assertEqual('User registered successfully', response.data.decode())

    def test_username_or_password_not_found(self):
        response = self.client.post('/register', headers={'Username': '', 'Password': 'testpass'})
        self.assertEqual(400, response.status_code)
        self.assertEqual('Username or password not found', response.data.decode())

        response = self.client.post('/register', headers={'Username': 'testuser', 'Password': ''})
        self.assertEqual(400, response.status_code)
        self.assertEqual('Username or password not found', response.data.decode())

    @patch('backend.app.routes.user_management.collection.find_one')
    def test_username_already_exists(self, mock_find):
        self.client.post('/register', headers={'Username': 'testuser 2', 'Password': 'testpass'})
        response = self.client.post('/register', headers={'Username': 'testuser 2', 'Password': 'testpass'})
        self.assertEqual(401, response.status_code)
        self.assertEqual('Username already exists', response.data.decode())

    @patch('backend.app.routes.user_management.collection.insert_one')
    def test_error_occurred(self, mock_insert):
        mock_insert.side_effect = Exception('Database error')
        response = self.client.post('/register', headers={'Username': 'testuser', 'Password': 'testpass'})
        self.assertEqual(500, response.status_code)
        self.assertIn('Error occurred: Database error', response.data.decode())

    @patch('backend.app.routes.user_management.collection.find_one')
    def test_user_logged_in_successfully(self, mock_find):
        mock_find.return_value = {'Username': 'testuser', 'Password': hashlib.sha256('testpass'.encode()).hexdigest()}
        response = self.client.post('/login', headers={'Username': 'testuser', 'Password': 'testpass'})
        self.assertEqual(200, response.status_code)
        self.assertEqual('User logged in successfully', response.data.decode())

    def test_invalid_username_or_password(self):
        response = self.client.post('/login', headers={'Username': '', 'Password': 'testpass'})
        self.assertEqual(400, response.status_code)
        self.assertEqual('Invalid username or password', response.data.decode())

        response = self.client.post('/login', headers={'Username': 'testuser', 'Password': ''})
        self.assertEqual(400, response.status_code)
        self.assertEqual('Invalid username or password', response.data.decode())

    @patch('backend.app.routes.user_management.collection.find_one')
    def test_login_username_or_password_not_found(self, mock_find):
        mock_find.return_value = None
        response = self.client.post('/login', headers={'Username': 'testuser', 'Password': 'testpass'})
        self.assertEqual(401, response.status_code)
        self.assertEqual('Username or password not found', response.data.decode())

    @patch('backend.app.routes.user_management.collection.find_one')
    def test_login_error_occurred(self, mock_find):
        mock_find.side_effect = Exception('Database error')
        response = self.client.post('/login', headers={'Username': 'testuser', 'Password': 'testpass'})
        self.assertEqual(500, response.status_code)
        self.assertIn('Error occurred: Database error', response.data.decode())