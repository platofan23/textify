import hashlib
import configparser
from pymongo import MongoClient
from flask_restful import Resource, reqparse

# Konfiguration laden
config = configparser.ConfigParser()
config.read('../config/config.ini')

# Verbindung zur MongoDB
client = MongoClient(config['MONGO_DB']['CONNECTION_STRING'])
db = client[config['MONGO_DB']['MONGO_DATABASE']]
collection = db[config['MONGO_DB']['MONGO_USERS_COLLECTION']]


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
            user = {
                'Username': username,
                'Password': hashlib.sha256(password.encode()).hexdigest()
            }
            collection.insert_one(user)
            return {'message': 'User registered successfully'}, 201

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
            # Benutzer und Passwort prüfen
            user = collection.find_one({
                'Username': username,
                'Password': hashlib.sha256(password.encode()).hexdigest()
            })

            if user:
                return {'message': 'User logged in successfully'}, 200
            return {'error': 'Invalid username or password'}, 401

        except Exception as e:
            return {'error': f'Error occurred: {str(e)}'}, 500
