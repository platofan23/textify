from flask import request
from flask_restful import Resource

from backend.app.services.service_translation import translate_file, translate_text


# Translate PDF file endpoint
class TranslateFile(Resource):
    """
    Handles the translation of PDF files by receiving a base64 encoded file,
    translating it page by page, and returning the result.
    """

    def post(self):
        # Get JSON-Object data from the request
        json_data = request.get_json()

        # Check if JSON data contains the 'data' object
        if not json_data or 'data' not in json_data:
            return {"error": "Missing data object"}, 400

        # Extract parameters from the JSON object
        data = json_data['data']
        model = data.get('model')
        sourcelanguage = data.get('sourcelanguage')
        targetlanguage = data.get('targetlanguage')
        file = data.get('file')

        # Validate required parameters
        if not model or not sourcelanguage or not targetlanguage or not file:
            return {"error": "Missing required parameters"}, 400

        try:
            # Perform translation of the PDF file
            result = translate_file(file, model, sourcelanguage, targetlanguage)

            # Return translation result if successful
            if result:
                return {"translation": result}, 200
            else:
                return {"error": "Translation failed"}, 500
        except ValueError as e:
            return {"error": f"Invalid input: {str(e)}"}, 422
        except ConnectionError as e:
            return {"error": f"Translation service unavailable: {str(e)}"}, 503
        except Exception as e:
            # Handle any internal server error
            return {"error": f"Internal Server Error: {str(e)}"}, 500


# Translate text endpoint
class TranslateText(Resource):
    """
    Handles the translation of plain text by receiving text along with source and target languages,
    and returning the translated result.
    """

    def post(self):
        # Get JSON-Object data from the request
        json_data = request.get_json()

        # Check if JSON data contains the 'data' object
        if not json_data or 'data' not in json_data:
            return {"error": "Missing data object"}, 400

        # Extract parameters from the JSON object
        data = json_data['data']
        model = data.get('model')
        sourcelanguage = data.get('sourcelanguage')
        targetlanguage = data.get('targetlanguage')
        text = data.get('text')

        # Validate required parameters
        if not model or not sourcelanguage or not targetlanguage or not text:
            return {"error": "Missing required parameters"}, 400

        try:
            # Perform translation of the input text
            result = translate_text(model, sourcelanguage, targetlanguage, text)

            # Return translation result if successful
            if result:
                return {"translation": result}, 200
            else:
                return {"error": "Translation failed"}, 500
        except ValueError as e:
            return {"error": f"Invalid input: {str(e)}"}, 422
        except ConnectionError as e:
            return {"error": f"Translation service unavailable: {str(e)}"}, 503
        except Exception as e:
            # Handle any internal server error
            return {"error": f"Internal Server Error: {str(e)}"}, 500
