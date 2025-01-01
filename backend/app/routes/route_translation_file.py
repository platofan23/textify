import os
from flask import request, send_file
from flask_restful import Resource


class TranslateFile(Resource):
    def post(self):
        # Parameter aus der Anfrage abrufen
        filename = request.args.get('filename')
        user = request.args.get('user')
        title = request.args.get('title')
        model = request.args.get('model')

