import secrets
from threading import Thread
from random import random
from datetime import datetime, timedelta

from flask import make_response
from flask_restful import Resource, reqparse
from argon2 import PasswordHasher

from backend.app.utils import Logger
from backend.app.utils.util_mongo_manager import MongoDBManager
from backend.app.utils.util_config_manager import ConfigManager
from backend.app.utils.util_crypt import Crypto_Manager


class RegisterUser(Resource):
    def __init__(self, mongo_manager: MongoDBManager, config_manager: ConfigManager, crypto_manager: Crypto_Manager):
        """
        Handles user registration, ECC key generation, and password hashing.
        """
        self.mongo_manager = mongo_manager
        self.config_manager = config_manager
        self.crypto_manager = crypto_manager

        # Retrieve user collection name from config
        self.users_collection_name = self.config_manager.get_config_value("MONGO_DB", "MONGO_USERS_COLLECTION", str)
        self.collection = self.mongo_manager.get_collection(self.users_collection_name)

        # Initialize password hasher
        self.ph = PasswordHasher()

    def post(self):
        """
        Handles user registration by hashing passwords, generating ECC keys, and storing the user.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('Username', location='headers', required=True, help="Username is required")
        parser.add_argument('Password', location='headers', required=True, help="Password is required")
        args = parser.parse_args()

        username = args['Username']
        password = args['Password']

        try:
            # Check if user already exists
            if self.collection.find_one({'Username': username}):
                return {'error': 'Username already exists'}, 409

            # Hash the password and generate ECC keys
            hashed_password = self.ph.hash(password)
            public_key_str = self.crypto_manager.generate_ecc_keys(username)

            # Create user document
            user = {
                'Username': username,
                'Password': hashed_password,
                "PublicKey": public_key_str,
            }
            self.mongo_manager.insert_document(self.users_collection_name, user)

            response = {
                'Message': 'User registered successfully',
                'Username': username,
                'AuthorizationKey': self.crypto_manager.add_key(username, self.collection)
            }
            return make_response(response, 200)

        except Exception as e:
            Logger.error(f"Error during registration: {e}")
            return {'error': f'Error occurred: {str(e)}'}, 500


class LoginUser(Resource):
    def __init__(self, mongo_manager: MongoDBManager, config_manager: ConfigManager, crypto_manager: Crypto_Manager):
        """
        Handles user authentication and authorization key generation.
        """
        self.mongo_manager = mongo_manager
        self.config_manager = config_manager
        self.crypto_manager = crypto_manager

        self.users_collection_name = self.config_manager.get_config_value("MONGO_DB", "MONGO_USERS_COLLECTION", str)
        self.collection = self.mongo_manager.get_collection(self.users_collection_name)
        self.ph = PasswordHasher()

    def post(self):
        """
        Handles user login by verifying passwords and generating authorization keys.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('Username', location='headers', required=True, help="Username is required")
        parser.add_argument('Password', location='headers', required=True, help="Password is required")
        args = parser.parse_args()

        username = args['Username']
        password = args['Password']

        try:
            user = self.collection.find_one({'Username': username})
            if user and self.ph.verify(user['Password'], password):
                # Occasionally clean up expired keys
                if random() <= 0.1:
                    Thread(target=self.crypto_manager.delete_expired_keys, args=(self.collection,)).start()

                response = {
                    'Message': 'User logged in successfully',
                    'Username': username,
                    'AuthorizationKey': self.crypto_manager.add_key(username, self.collection)
                }
                return make_response(response, 200)
            return {'error': 'Username or password not found'}, 401

        except Exception as e:
            Logger.error(f"Error during login: {e}")
            return {'error': f'Error occurred: {str(e)}'}, 500
