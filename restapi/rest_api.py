
import configparser
import os
import shutil
from io import BytesIO
from flask import Flask, request, jsonify, send_file
from pymongo import MongoClient
import gridfs
from ocr.multi_ocr import MultiOcr

# Load configuration from config.ini
config = configparser.ConfigParser()
config.read('../config.ini')

# Set up Flask
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = config['REST']['UPLOAD_FOLDER']
app.config['MAX_CONTENT_LENGTH'] = int(config['REST']['MAX_CONTENT_LENGTH_MB']) * 1024 * 1024 # Set max file size to xMB
MAX_TOTAL_SIZE = int(config['REST']['MAX_TOTAL_SIZE_GB']) * 1024 * 1024 * 1024 # Set max total file size to xGB
ALLOWED_EXTENSIONS = set(config['REST']['ALLOWED_EXTENSIONS'].replace(" ", "").split(','))

# MongoDB connection
client = MongoClient(config['MONGO_DB']['MONGO_URI'])
db = client[config['MONGO_DB']['MONGO_UPLOADS']]
fs = gridfs.GridFS(db, collection=config['MONGO_DB']['MONGO_COLLECTION'])

easy_ocr = MultiOcr()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

'''
Route to upload files
POST request should contain:
- 'files' part with the files to be uploaded
- 'User' part with the user name
- 'Title' part with the title of the files
'''
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

    # Create user folder and title folder if they don't exist
    user_folder_path = os.path.join(app.config['UPLOAD_FOLDER'], request.headers.get("User"))
    os.makedirs(user_folder_path, exist_ok=True) # Create user folder if it doesn't exist
    title_folder_path = os.path.join(user_folder_path, request.headers.get("Title"))
    os.makedirs(title_folder_path, exist_ok=True) # Create title folder if it doesn't exist


    for file in files:

        if file.filename == '':
            return 'No selected file'

        if allowed_file(file.filename):
            total_size += len(file.read())
            file.seek(0)

            # Check if total file size exceeds limit
            if total_size > MAX_TOTAL_SIZE:
                # Delete files already uploaded
                shutil.rmtree(title_folder_path)
                return 'Total file size exceeds ' + str(MAX_TOTAL_SIZE) + ' bytes'

            file.save(os.path.join(title_folder_path, file.filename))  # Save file to user folder

        else:
            return 'Invalid file type'

    return 'Files uploaded successfully'

'''
Route to download a saved file
'''
@app.route('/download_file', methods=['GET'])
def get_file():
    filename = request.args.get('filename')
    user = request.args.get('user')
    title = request.args.get('title')
    if not filename or not user or not title:
        return 'File not found', 404

    try:
        # Retrieve the file from GridFS using the filename
        user_folder_path = os.path.join(app.config['UPLOAD_FOLDER'], user)
        title_folder_path = os.path.join(user_folder_path, title)
        file_path = os.path.join(title_folder_path, filename)

        # Return the file as a response
        return send_file(file_path, download_name=filename, as_attachment=True)
    except Exception as e:
        return f'Error occurred: {str(e)}', 500

'''
Route to read the text from a saved file
'''
@app.route('/read_file', methods=['GET'])
def read_file():
    filename = request.args.get('filename')
    user = request.args.get('user')
    title = request.args.get('title')
    if not filename or not user or not title:
        return 'File not found', 404

    try:
        # Retrieve the file from GridFS using the filename
        user_folder_path = os.path.join(app.config['UPLOAD_FOLDER'], user)
        title_folder_path = os.path.join(user_folder_path, title)
        file_path = os.path.join(title_folder_path, filename)

        # Perform OCR on the file
        text = easy_ocr.read_text(file_path)

        return jsonify(text)
    except Exception as e:
        return f'Error occurred: {str(e)}', 500

if __name__ == '__main__':
    app.run()
