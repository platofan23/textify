import json
import secrets
from threading import Thread
from random import random
from datetime import datetime, timedelta

from Crypto.PublicKey import ECC
from flask import make_response
from flask_restful import Resource, reqparse
from argon2 import PasswordHasher

from backend.app.utils import Logger
from backend.app.utils.util_mongo_manager import MongoDBManager
from backend.app.utils.util_config_manager import ConfigManager


class RegisterUser(Resource):
    def __init__(self, mongo_manager: MongoDBManager, config_manager: ConfigManager):
        """
        Konstruktor, der die Abhängigkeiten injiziert und die benötigten Attribute initialisiert.
        """
        self.mongo_manager = mongo_manager
        self.config_manager = config_manager

        # Hole den Namen der Benutzer-Collection aus der Konfiguration
        self.users_collection_name = self.config_manager.get_config_value(
            "MONGO_DB", "MONGO_USERS_COLLECTION", str
        )
        # Abrufen der Collection über den MongoDBManager
        self.collection = self.mongo_manager.get_collection(self.users_collection_name)

        # Initialisiere den Passwort-Hasher
        self.ph = PasswordHasher()

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('Username', location='headers', required=True, help="Username is required")
        parser.add_argument('Password', location='headers', required=True, help="Password is required")
        args = parser.parse_args()

        username = args['Username']
        password = args['Password']

        try:
            # Prüfe, ob der Benutzer bereits existiert
            if self.collection.find_one({'Username': username}):
                return {'error': 'Username already exists'}, 409

            # Erzeuge Passwort-Hash und ECC-Schlüssel
            hashed_password = self.ph.hash(password)
            public_key_str = self._generate_keys(username)

            # Erstelle den Benutzer-Datensatz
            user = {
                'Username': username,
                'Password': hashed_password,
                "PublicKey": public_key_str,
            }
            self.mongo_manager.insert_document(self.users_collection_name, user)

            response = {
                'Message': 'User registered successfully',
                'Username': username,
                'AuthorizationKey': self.add_key(username)
            }
            return make_response(response, 200)

        except Exception as e:
            Logger.error(f"Error during registration: {e}")
            return {'error': f'Error occurred: {str(e)}'}, 500

    def _generate_keys(self, username: str) -> str:
        # Generiere ein ECC-Schlüsselpaar
        private_key = ECC.generate(curve='secp256r1')
        Logger.info('Generated ECC keys')

        # Speichere den privaten Schlüssel in einer JSON-Datei
        private_keys_path = './keys/private_keys.json'
        try:
            with open(private_keys_path, 'r+') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []
                if not isinstance(data, list):
                    data = []
                data.append({'user': username, 'private_key': private_key.export_key(format='PEM')})
                f.seek(0)
                json.dump(data, f)
                f.truncate()
        except FileNotFoundError:
            # Falls die Datei nicht existiert, lege sie neu an
            with open(private_keys_path, 'w') as f:
                data = [{'user': username, 'private_key': private_key.export_key(format='PEM')}]
                json.dump(data, f)

        return private_key.public_key().export_key(format='PEM')

    def add_key(self, username: str) -> str:
        # Erzeuge einen neuen Schlüssel, gültig für 7 Tage
        expiration_date = datetime.now() + timedelta(days=7)
        key = secrets.token_hex(32)
        self.collection.update_one(
            {'Username': username},
            {'$push': {'AuthorizationKeys': {'Key': key, 'ExpiresAt': expiration_date}}}
        )
        return key


class LoginUser(Resource):
    def __init__(self, mongo_manager: MongoDBManager, config_manager: ConfigManager):
        self.mongo_manager = mongo_manager
        self.config_manager = config_manager

        self.users_collection_name = self.config_manager.get_config_value(
            "MONGO_DB", "MONGO_USERS_COLLECTION", str
        )
        self.collection = self.mongo_manager.get_collection(self.users_collection_name)
        self.ph = PasswordHasher()

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('Username', location='headers', required=True, help="Username is required")
        parser.add_argument('Password', location='headers', required=True, help="Password is required")
        args = parser.parse_args()

        username = args['Username']
        password = args['Password']

        try:
            user = self.collection.find_one({'Username': username})
            if user and self.ph.verify(user['Password'], password):
                # Starte asynchron das Löschen abgelaufener Schlüssel
                if random() <= 0.1:
                    Thread(target=self.delete_expired_keys).start()

                response = {
                    'Message': 'User logged in successfully',
                    'Username': username,
                    'AuthorizationKey': self.add_key(username)
                }
                return make_response(response, 200)
            return {'error': 'Username or password not found'}, 401

        except Exception as e:
            Logger.error(f"Error during login: {e}")
            return {'error': f'Error occurred: {str(e)}'}, 500

    def add_key(self, username: str) -> str:
        expiration_date = datetime.now() + timedelta(days=7)
        key = secrets.token_hex(32)
        self.collection.update_one(
            {'Username': username},
            {'$push': {'AuthorizationKeys': {'Key': key, 'ExpiresAt': expiration_date}}}
        )
        return key

    def delete_expired_keys(self):
        current_time = datetime.now()
        Logger.info('Deleting expired authorization keys')
        self.collection.update_many(
            {},
            {'$pull': {'AuthorizationKeys': {'ExpiresAt': {'$lt': current_time}}}}
        )
