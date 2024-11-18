import os
import shutil

from flask import Flask, request, jsonify

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '../uploads'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB per file
MAX_TOTAL_SIZE = 10 * 1024 * 1024 * 1024  # 10GB total size

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

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

    # Create user folder and title folder if they don't exist
    user_folder_path = os.path.join(app.config['UPLOAD_FOLDER'], request.headers.get("User"))
    os.makedirs(user_folder_path, exist_ok=True) # Create user folder if it doesn't exist
    title_folder_path = os.path.join(user_folder_path, request.headers.get("Title"))
    os.makedirs(title_folder_path, exist_ok=True) # Create title folder if it doesn't exist

    for file in files:
        if file.filename == '':
            return 'No selected file'
        if file and allowed_file(file.filename):
            total_size += len(file.read())
            file.seek(0)  # Reset file pointer after reading
            if total_size > MAX_TOTAL_SIZE:
                # Delete title folder if total file size exceeds 10GB
                shutil.rmtree(title_folder_path)
                return 'Total file size exceeds 10GB'
            file.save(os.path.join(title_folder_path, file.filename)) # Save file to user folder
        else:
            return 'Invalid file type or file too large'
    return 'Files uploaded successfully'

if __name__ == '__main__':
    app.run()
