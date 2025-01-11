import os
import configparser

from flask import jsonify
from flask_restful import Resource, reqparse
from backend.app.services import multi_reader

# Konfiguration laden
config = configparser.ConfigParser()
config.read('./config/config.ini')
UPLOAD_FOLDER = config['REST']['UPLOAD_FOLDER']


class ReadFile(Resource):
    def get(self):
        # Argumente aus der Anfrage parsen
        parser = reqparse.RequestParser()
        parser.add_argument('filename', type=str, required=True, help="Filename is required")
        parser.add_argument('user', type=str, required=True, help="User is required")
        parser.add_argument('title', type=str, required=True, help="Title is required")
        parser.add_argument('model', type=str, required=False, default='default_model')
        args = parser.parse_args()

        filename = args['filename']
        user = args['user']
        title = args['title']
        model = args['model']

        try:
            # Pfade zusammenbauen
            user_folder_path = os.path.join(UPLOAD_FOLDER, user)
            title_folder_path = os.path.join(user_folder_path, title)
            file_path = os.path.join(title_folder_path, filename)

            # Überprüfung, ob die Datei existiert
            if not os.path.exists(file_path):
                return {'error': 'File not found'}, 404

            # Datei mit OCR lesen
            text = multi_reader(file_path, model=model)

            # Text in JSON zurückgeben
            return jsonify({'text': text})

        except Exception as e:
            return {'error': f'Error occurred: {str(e)}'}, 500

