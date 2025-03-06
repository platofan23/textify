import os
import configparser
from flask import jsonify
from flask_restful import Resource, reqparse

from backend.app.services.ocr import multi_reader
from backend.app.utils.util_logger import Logger  # Assuming Logger is available

# Load configuration
config = configparser.ConfigParser()
config.read('./config/config.ini')
UPLOAD_FOLDER = config['REST']['UPLOAD_FOLDER']

class ReadFile(Resource):
    """
    Resource for reading a file using OCR.
    """

    @staticmethod
    def get():
        """
        Handles GET requests to perform OCR on a file.

        Expected query parameters:
            - filename: Name of the file to process.
            - user: Username of the file owner.
            - title: Title associated with the file.
            - model (optional): The OCR model to use (default is 'default_model').

        Returns:
            A JSON response containing the extracted text or an error message with the corresponding HTTP status code.
        """
        # Parse required parameters from the request.
        parser = reqparse.RequestParser()
        parser.add_argument('filename', type=str, required=True, help="Filename is required")
        parser.add_argument('user', type=str, required=True, help="User is required")
        parser.add_argument('title', type=str, required=True, help="Title is required")
        parser.add_argument('model', type=str, required=False, default='default_model', help="OCR model (optional)")
        args = parser.parse_args()

        filename = args['filename']
        user = args['user']
        title = args['title']
        model = args['model']

        try:
            # Build file paths based on the configuration and provided parameters.
            user_folder_path = os.path.join(UPLOAD_FOLDER, user)
            title_folder_path = os.path.join(user_folder_path, title)
            file_path = os.path.join(title_folder_path, filename)

            # Check if the file exists.
            if not os.path.exists(file_path):
                Logger.error(f"File '{file_path}' not found for user '{user}' and title '{title}'.")
                return {'error': 'File not found'}, 404

            Logger.info(f"Starting OCR for file '{file_path}' using model '{model}'.")
            # Perform OCR on the file using the provided model.
            text = multi_reader(file_path, model=model)
            Logger.info(f"OCR completed successfully for file '{file_path}'.")

            # Return the extracted text as JSON.
            return jsonify({'text': text})

        except Exception as e:
            Logger.error(f"Error processing file '{filename}' for user '{user}' and title '{title}': {str(e)}")
            return {'error': f"Error occurred: {str(e)}"}, 500
