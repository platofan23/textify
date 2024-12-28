import configparser
import secrets
from datetime import datetime, timedelta
from random import random

from flask import Blueprint, request, jsonify, send_file, make_response
from pymongo import MongoClient
from argon2 import PasswordHasher
from threading import Thread

# Load configuration from config.ini
config = configparser.ConfigParser()
config.read('../../config.ini')

user_management_bp = Blueprint('user_management', __name__)

# Connect to MongoDB
client = MongoClient(config['MONGO_DB']['CONNECTION_STRING'])
db = client[config['MONGO_DB']['MONGO_DATABASE']]
collection = db[config['MONGO_DB']['MONGO_USERS_COLLECTION']]

# Initialize Argon2 Password Hasher
ph = PasswordHasher()

# User Registration Route
@user_management_bp.route('/register', methods=['POST'])
def user_register():
    username = request.headers.get('Username')
    password = request.headers.get('Password')
    if not username or not password:
        return 'Username or password not found', 400

    try:
        hashed_password = ph.hash(password)
        user = {
            'Username': username,
            'Password': hashed_password
        }

        if collection.find_one({'Username': username}):
            return 'Username already exists', 401

        collection.insert_one(user)
        response = make_response('User registered successfully', 200)
        response.headers['Authorization'] = add_key(username)
        return response

    except Exception as e:
        return f'Error occurred: {str(e)}', 500

# User Login Route
@user_management_bp.route('/login', methods=['POST'])
def user_login():
    username = request.headers.get('Username')
    password = request.headers.get('Password')
    if not username or not password:
        return 'Invalid username or password', 400

    try:
        user = collection.find_one({'Username': username})
        if user and ph.verify(user['Password'], password):

            # Delete expired keys with 10% probability
            if random() <= 0.1:
                Thread(target=delete_expired_keys).start()



            response = {'Message': 'User logged in successfully', 'Username': username, 'AuthorizationKey': add_key(username)}


            return make_response(response, 200)
        return 'Username or password not found', 401

    except Exception as e:
        return f'Error occurred: {str(e)}', 500

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