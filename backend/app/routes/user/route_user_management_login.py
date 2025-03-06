import secrets
from threading import Thread
from random import random
from flask import make_response
from flask_restful import Resource, reqparse
from argon2 import PasswordHasher

from backend.app.utils import Logger
from backend.app.utils.util_mongo_manager import MongoDBManager
from backend.app.utils.util_config_manager import ConfigManager
from backend.app.utils.util_crypt import Crypto_Manager

class LoginUser(Resource):
    """
    Resource for handling user authentication and authorization key generation.
    """
    def __init__(self, mongo_manager: MongoDBManager, config_manager: ConfigManager, crypto_manager: Crypto_Manager):
        """
        Initializes the LoginUser resource with MongoDB manager, configuration manager, and crypto manager.

        Args:
            mongo_manager (MongoDBManager): Instance of MongoDB manager.
            config_manager (ConfigManager): Instance of configuration manager.
            crypto_manager (Crypto_Manager): Instance of crypto manager.
        """
        self.mongo_manager = mongo_manager
        self.config_manager = config_manager
        self.crypto_manager = crypto_manager

        # Retrieve the collection name for users from configuration.
        self.users_collection_name = self.config_manager.get_config_value("MONGO_DB", "MONGO_USERS_COLLECTION", str)
        self.collection = self.mongo_manager.get_collection(self.users_collection_name)
        self.ph = PasswordHasher()

    def post(self):
        """
        Handles user login by verifying the password and generating an authorization key.

        Expected headers:
            - Username: The username of the user.
            - Password: The password of the user.

        Returns:
            A JSON response with the authorization key if successful, or an error message with an appropriate HTTP status code.
        """
        # Parse required headers.
        parser = reqparse.RequestParser()
        parser.add_argument('Username', location='headers', required=True, help="Username is required")
        parser.add_argument('Password', location='headers', required=True, help="Password is required")
        args = parser.parse_args()

        username = args['Username']
        password = args['Password']

        try:
            # Find the user document by username.
            user = self.collection.find_one({'Username': username})
            if user and self.ph.verify(user['Password'], password):
                # Occasionally clean up expired keys in a separate thread.
                if random() <= 0.1:
                    Thread(target=self.crypto_manager.delete_expired_keys, args=(self.collection,)).start()

                response = {
                    'Message': 'User logged in successfully',
                    'Username': username,
                    'AuthorizationKey': self.crypto_manager.add_key(username, self.collection)
                }
                Logger.info(f"User '{username}' logged in successfully.")
                return make_response(response, 200)

            Logger.warning(f"Login failed for username '{username}'. Invalid username or password.")
            return {'error': 'Username or password not found'}, 401

        except Exception as e:
            Logger.error(f"Error during login for user '{username}': {str(e)}")
            return {'error': f"Error occurred: {str(e)}"}, 500
