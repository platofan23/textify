import configparser
from flask import Blueprint, request, jsonify, send_file
import os
import shutil


# Load configuration from config.ini
config = configparser.ConfigParser()
config.read('../../config.ini')
MAX_TOTAL_SIZE = int(config['REST']['MAX_TOTAL_SIZE_GB']) * 1024 * 1024 * 1024
ALLOWED_EXTENSIONS = set(config['REST']['ALLOWED_EXTENSIONS'].replace(" ", "").split(','))
UPLOAD_FOLDER = config['REST']['UPLOAD_FOLDER']

file_manager_bp = Blueprint('files', __name__)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@file_manager_bp.route('/upload_files', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return 'No file part'
    if 'User' not in request.headers:
        return 'No user part'
    if 'Title' not in request.headers:
        return 'No title part'

    files = request.files.getlist('files')
    total_size = 0

    user_folder_path = os.path.join(UPLOAD_FOLDER, request.headers.get("User"))
    os.makedirs(user_folder_path, exist_ok=True)
    title_folder_path = os.path.join(user_folder_path, request.headers.get("Title"))
    os.makedirs(title_folder_path, exist_ok=True)

    for file in files:
        if file.filename == '':
            return 'No selected file'
        if allowed_file(file.filename):
            total_size += len(file.read())
            file.seek(0)
            if total_size > MAX_TOTAL_SIZE:
                shutil.rmtree(title_folder_path)
                return 'Total file size exceeds ' + str(MAX_TOTAL_SIZE) + ' bytes'
            file.save(os.path.join(title_folder_path, file.filename))
        else:
            return 'Invalid file type'
    return 'Files uploaded successfully'

@file_manager_bp.route('/download_file', methods=['GET'])
def get_file():
    filename = request.args.get('filename')
    user = request.args.get('user')
    title = request.args.get('title')
    if not filename or not user or not title:
        return 'File not found', 404
    try:
        user_folder_path = os.path.join(UPLOAD_FOLDER, user)
        title_folder_path = os.path.join(user_folder_path, title)
        file_path = os.path.join(title_folder_path, filename)
        return send_file(file_path, download_name=filename, as_attachment=True)
    except Exception as e:
        return f'Error occurred: {str(e)}', 500
