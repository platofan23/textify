import configparser
from flask import Blueprint, request, jsonify, send_file
from pymongo import MongoClient
import hashlib

from backend.app.services.multi_ocr import multi_reader

# Load configuration from config.ini
config = configparser.ConfigParser()
config.read('../../config.ini')


user_management_bp = Blueprint('user_management', __name__)

#Connect to MongoDB
client = MongoClient(config['MONGO_DB']['CONNECTION_STRING'])
db = client[config['MONGO_DB']['MONGO_DATABASE']]
collection = db[config['MONGO_DB']['MONGO_USERS_COLLECTION']]

# User Management Route
@user_management_bp.route('/register', methods=['POST'])
def user_register():
    username = request.headers.get('Username')
    password = request.headers.get('Password')
    if not username or not password:
        return 'Username or password not found', 400

    try:
        user = {
            'Username': username,
            'Password': hashlib.sha256(password.encode()).hexdigest()
        }

        if collection.find_one({'Username': username}):
            return 'Username already exists', 401


        collection.insert_one(user)
        return 'User registered successfully', 200


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
        user = collection.find_one({'Username': username, 'Password': hashlib.sha256(password.encode()).hexdigest()})
        if user:
            return 'User logged in successfully', 200
        return 'Username or password not found', 401

    except Exception as e:
        return f'Error occurred: {str(e)}', 500