import hashlib
import configparser
import secrets
from random import random
from threading import Thread

from pymongo import MongoClient
from flask_restful import Resource, reqparse
from argon2 import PasswordHasher
from datetime import datetime, timedelta
from flask import make_response

# Konfiguration laden
config = configparser.ConfigParser()
config.read('../config/config.ini')

# Verbindung zur MongoDB
client = MongoClient(config['MONGO_DB']['CONNECTION_STRING'])
db = client[config['MONGO_DB']['MONGO_DATABASE']]
collection = db[config['MONGO_DB']['MONGO_USERS_COLLECTION']]

# Initialize Argon2 Password Hasher
ph = PasswordHasher()


# Ressource für Benutzerregistrierung
class RegisterUser(Resource):
    def post(self):
        # Argumente aus den Headern parsen
        parser = reqparse.RequestParser()
        parser.add_argument('Username', location='headers', required=True, help="Username is required")
        parser.add_argument('Password', location='headers', required=True, help="Password is required")
        args = parser.parse_args()

        username = args['Username']
        password = args['Password']

        try:
            # Benutzer prüfen, ob existiert
            if collection.find_one({'Username': username}):
                return {'error': 'Username already exists'}, 409

            # Benutzer erstellen
            hashed_password = ph.hash(password)
            user = {
                'Username': username,
                'Password': hashed_password
            }
            collection.insert_one(user)
            response = {'Message': 'User registered successfully', 'Username': username,
                        'AuthorizationKey': add_key(username)}

            return make_response(response, 200)

        except Exception as e:
            return {'error': f'Error occurred: {str(e)}'}, 500


# Ressource für Benutzeranmeldung
class LoginUser(Resource):
    def post(self):
        # Argumente parsen
        parser = reqparse.RequestParser()
        parser.add_argument('Username', location='headers', required=True, help="Username is required")
        parser.add_argument('Password', location='headers', required=True, help="Password is required")
        args = parser.parse_args()

        username = args['Username']
        password = args['Password']

        try:
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