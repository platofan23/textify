from flask_restful import Resource, reqparse

from backend.app.services.stt import SpeechToTextService
from backend.app.utils.util_logger import Logger


class SpeechToText(Resource):
    """
    Endpoint for Speech-to-Text conversion.

    Accepts a WAV audio file via a POST request and returns the transcribed text.
    """

    def __init__(self, config_manager, cache_manager):
        """
        Initializes the SpeechToText endpoint with required services.

        Args:
            config_manager: The configuration manager instance.
            cache_manager: The cache manager instance.
        """
        self.config_manager = config_manager
        self.stt_service = SpeechToTextService(config_manager, cache_manager)
        Logger.info("SpeechToText endpoint initialized.")

    def post(self):
        """
        Handles POST requests for speech-to-text conversion.

        Expects form-data:
            - audio_file: The WAV audio file to be transcribed.

        Returns:
            dict: A JSON object with the transcription on success,
                  or an error message with the appropriate HTTP status code.
        """
        Logger.info("POST request received for speech-to-text conversion.")
        parser = reqparse.RequestParser()
        parser.add_argument('audio_file', type=lambda x: x, location='files', required=True,
                            help="Audio file is required")
        args = parser.parse_args()
        audio_file = args['audio_file']

        try:
            transcription = self.stt_service.transcribe_audio(audio_file)
            Logger.info("Speech-to-text conversion completed successfully.")
            return {"transcription": transcription}, 200
        except Exception as e:
            Logger.error(f"Internal Server Error during speech-to-text processing: {str(e)}")
            return {"error": f"Internal Server Error: {str(e)}"}, 500