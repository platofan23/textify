import json
import os
import configparser
import secrets
from Crypto.PublicKey import ECC
from Crypto.IO import PEM
from random import random
from threading import Thread
from pymongo import MongoClient
from flask_restful import Resource, reqparse
from argon2 import PasswordHasher
from datetime import datetime, timedelta
from flask import make_response

from backend.app.utils import Logger

# Konfiguration laden
config = configparser.ConfigParser()
config.read('./config/config.ini')
if os.getenv("IsDocker"):
    config.read('./config/docker.ini')

# Verbindung zur MongoDB
client = MongoClient(config['MONGO_DB']['CONNECTION_STRING'])
db = client[config['MONGO_DB']['MONGO_DATABASE']]
collection = db[config['MONGO_DB']['MONGO_USERS_COLLECTION']]

# Initialize Argon2 Password Hasher
ph = PasswordHasher()


# Ressource für Benutzerregistrierung
class RegisterUser(Resource):
    def post(self):
        """
        Register a new user.
        """

        # Parse arguments
        parser = reqparse.RequestParser()
        parser.add_argument('Username', location='headers', required=True, help="Username is required")
        parser.add_argument('Password', location='headers', required=True, help="Password is required")
        args = parser.parse_args()

        username = args['Username']
        password = args['Password']

        try:
            # Check if username already exists
            if collection.find_one({'Username': username}):
                return {'error': 'Username already exists'}, 409

            # Generate password hash and keys
            hashed_password = ph.hash(password)
            public_key_str = self._generate_keys(username)

            # Create user
            user = {
                'Username': username,
                'Password': hashed_password,
                "PublicKey": public_key_str,
            }
            collection.insert_one(user)

            response = {'Message': 'User registered successfully', 'Username': username,
                        'AuthorizationKey': add_key(username)}

            return make_response(response, 200)

        except Exception as e:
            return {'error': f'Error occurred: {str(e)}'}, 500

    def _generate_keys(self, username):

        # Generate ECC private key
        private_key = ECC.generate(curve='secp256r1')
        Logger.info(f'Generated keys')

        with open('./keys/private_keys.json', 'r+') as f:
            data = json.load(f)
            if not isinstance(data, list):
                data = []
            data.append({'user': username, 'private_key': private_key.export_key(format='PEM')})
            f.seek(0)
            json.dump(data, f)


        return private_key.public_key().export_key(format='PEM')



class LoginUser(Resource):
    def post(self):
        # Parse arguments
        parser = reqparse.RequestParser()
        parser.add_argument('Username', location='headers', required=True, help="Username is required")
        parser.add_argument('Password', location='headers', required=True, help="Password is required")
        args = parser.parse_args()

        username = args['Username']
        password = args['Password']


        try:
            # Check if user exists and password is correct
            user = collection.find_one({'Username': username})
            if user and ph.verify(user['Password'], password):

                # Delete expired keys with 10% probability
                if random() <= 0.1:
                    Thread(target=delete_expired_keys).start()

                response = {'Message': 'User logged in successfully', 'Username': username,
                            'AuthorizationKey': add_key(username)}

                return make_response(response, 200)
            return 'Username or password not found', 401

        except Exception as e:
            return {'error': f'Error occurred: {str(e)}'}, 500


def add_key(username):
    expiration_date = datetime.now() + timedelta(days=7)  # Set expiration date to 7 days from now
    key = secrets.token_hex(32)
    collection.update_one(
        {'Username': username},
        {'$push': {'AuthorizationKeys': {'Key': key, 'ExpiresAt': expiration_date}}}
    )
    return key

# Delete expired keys
def delete_expired_keys():
    current_time = datetime.now()
    print('Deleting expired keys')
    collection.update_many(
        {},
        {'$pull': {'AuthorizationKeys': {'ExpiresAt': {'$lt': current_time}}}}
    )