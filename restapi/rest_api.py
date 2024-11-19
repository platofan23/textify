
import configparser
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

    file_ids = []

    for file in files:

        if file.filename == '':
            return 'No selected file'

        if allowed_file(file.filename):
            total_size += len(file.read())
            file.seek(0)

            # Check if total file size exceeds limit
            if total_size > MAX_TOTAL_SIZE:
                # Delete files already uploaded
                for file_id in file_ids:
                    fs.delete(file_id)
                return 'Total file size exceeds ' + str(MAX_TOTAL_SIZE) + ' bytes'

            file_ids.append(fs.put(file, filename=file.filename, user=request.headers.get("User")
                                   , title=request.headers.get("Title")))

        else:
            return 'Invalid file type'

    return 'Files uploaded successfully'


@app.route('/download_file', methods=['GET'])
def get_file():
    filename = request.args.get('filename')
    if not filename:
        return 'No filename provided', 400

    try:
        # Retrieve the file from GridFS using the filename
        grid_out = fs.find_one({'filename': filename})
        if not grid_out:
            return 'File not found', 404

        # Return the file as a response
        return send_file(BytesIO(grid_out.read()), download_name=filename, as_attachment=True)
    except Exception as e:
        return f'Error occurred: {str(e)}', 500


@app.route('/read_file', methods=['GET'])
def read_file():
    filename = request.args.get('filename')
    if not filename:
        return 'No filename provided', 400

    try:
        # Retrieve the file from GridFS using the filename
        grid_out = fs.find_one({'filename': filename})
        if not grid_out:
            return 'File not found', 404

        # Perform OCR on the file
        text = easy_ocr.read_text(grid_out.read())



        return jsonify(text)
    except Exception as e:
        return f'Error occurred: {str(e)}', 500

if __name__ == '__main__':
    app.run()
