from flask import make_response
from flask_restful import Resource, reqparse
from argon2 import PasswordHasher

from backend.app.utils import Logger
from backend.app.utils.util_mongo_manager import MongoDBManager
from backend.app.utils.util_config_manager import ConfigManager
from backend.app.utils.util_crypt import Crypto_Manager

class RegisterUser(Resource):
    """
    Resource for handling user registration, ECC key generation, and password hashing.
    """
    def __init__(self, mongo_manager: MongoDBManager, config_manager: ConfigManager, crypto_manager: Crypto_Manager):
        """
        Initializes the RegisterUser resource with MongoDB, configuration, and crypto managers.

        Args:
            mongo_manager (MongoDBManager): Instance of MongoDB manager.
            config_manager (ConfigManager): Instance of configuration manager.
            crypto_manager (Crypto_Manager): Instance of crypto manager.
        """
        self.mongo_manager = mongo_manager
        self.config_manager = config_manager
        self.crypto_manager = crypto_manager

        # Retrieve user collection name from configuration.
        self.users_collection_name = self.config_manager.get_config_value("MONGO_DB", "MONGO_USERS_COLLECTION", str)
        self.collection = self.mongo_manager.get_collection(self.users_collection_name)

        # Initialize password hasher.
        self.ph = PasswordHasher()

    def post(self):
        """
        Handles user registration by hashing the password, generating ECC keys, and storing the user record.

        Expected headers:
            - Username: The desired username.
            - Password: The password for the account.

        Returns:
            A JSON response containing a success message, username, and authorization key on success,
            or an error message with the appropriate HTTP status code on failure.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('Username', location='headers', required=True, help="Username is required")
        parser.add_argument('Password', location='headers', required=True, help="Password is required")
        args = parser.parse_args()

        username = args['Username']
        password = args['Password']

        try:
            # Check if the user already exists.
            if self.collection.find_one({'Username': username}):
                Logger.warning(f"Registration attempt failed: Username '{username}' already exists.")
                return {'error': 'Username already exists'}, 409

            # Hash the password.
            hashed_password = self.ph.hash(password)
            # Generate ECC keys (public key as string).
            public_key_str = self.crypto_manager.generate_ecc_keys(username)

            # Create user document.
            user = {
                'Username': username,
                'Password': hashed_password,
                'PublicKey': public_key_str,
            }
            self.mongo_manager.insert_document(self.users_collection_name, user)

            response = {
                'Message': 'User registered successfully',
                'Username': username,
                'AuthorizationKey': self.crypto_manager.add_key(username, self.collection)
            }
            Logger.info(f"User '{username}' registered successfully.")
            return make_response(response, 200)

        except Exception as e:
            Logger.error(f"Error during registration for user '{username}': {str(e)}")
            return {'error': f"Error occurred: {str(e)}"}, 500
