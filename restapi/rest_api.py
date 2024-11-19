import os
import shutil
import configparser
from flask import Flask, request, jsonify

# Load configuration from config.ini
config = configparser.ConfigParser()
config.read('../config.ini')


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = config['REST']['UPLOAD_FOLDER']
app.config['MAX_CONTENT_LENGTH'] = int(config['REST']['MAX_CONTENT_LENGTH_MB']) * 1024 * 1024 # Set max file size to xMB
MAX_TOTAL_SIZE = int(config['REST']['MAX_TOTAL_SIZE_GB']) * 1024 * 1024 * 1024 # Set max total file size to xGB
ALLOWED_EXTENSIONS = set(config['REST']['ALLOWED_EXTENSIONS'].replace(" ", "").split(','))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload_files', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return 'No file part'
    if 'User' not in request.headers:
        return 'No user part'
    if 'Title' not in request.headers:
        return 'No title part'

    files = request.files.getlist('files')
    total_size = 0

    user_folder_path = os.path.join(app.config['UPLOAD_FOLDER'], request.headers.get("User"))
    os.makedirs(user_folder_path, exist_ok=True)
    title_folder_path = os.path.join(user_folder_path, request.headers.get("Title"))
    os.makedirs(title_folder_path, exist_ok=True)

    for file in files:
        if file.filename == '':
            return 'No selected file'
        if file and allowed_file(file.filename):
            total_size += len(file.read())
            file.seek(0)
            if total_size > MAX_TOTAL_SIZE:
                shutil.rmtree(title_folder_path)
                return 'Total file size exceeds 10GB'
            file.save(os.path.join(title_folder_path, file.filename))
        else:
            return 'Invalid file type or file too large'
    return 'Files uploaded successfully'

if __name__ == '__main__':
    app.run()
