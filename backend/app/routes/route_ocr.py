import configparser
from flask import Blueprint, request, jsonify, send_file
import os
from backend.app.services.service_ocr import multi_reader

# Load configuration from config.ini
config = configparser.ConfigParser()
config.read('../../config.ini')
UPLOAD_FOLDER = config['REST']['UPLOAD_FOLDER']

ocr_bp = Blueprint('ocr', __name__)



@ocr_bp.route('/read_file', methods=['GET'])
def read_file():
    filename = request.args.get('filename')
    user = request.args.get('user')
    title = request.args.get('title')
    model = request.args.get('model')

    if not filename or not user or not title:
        return 'File not found', 404


    try:
        user_folder_path = os.path.join(UPLOAD_FOLDER, user)
        title_folder_path = os.path.join(user_folder_path, title)
        file_path = os.path.join(title_folder_path, filename)

        text = multi_reader(file_path, model=model)
        return jsonify(text)

    except Exception as e:
        return f'Error occurred: {str(e)}', 500