from flask import request, send_file
from flask_restful import Resource
from backend.app.services.tts import TTSService
from backend.app.utils.util_logger import Logger

class TTS(Resource):
    """
    Resource for Text-to-Speech (TTS) synthesis.
    """
    def __init__(self, config_manager, cache_manager):
        """
        Initializes the TTS resource with required services.

        Args:
            config_manager: The configuration manager instance.
            cache_manager: The cache manager instance.
        """
        super().__init__()
        self.config_manager = config_manager
        self.tts_service = TTSService(config_manager, cache_manager)
        Logger.info("TTS instance initialized.")

    def post(self):
        """
        Handles POST requests for TTS synthesis.

        Expects a JSON payload with a 'data' object containing:
            - text: The text to be synthesized.
            - model (optional): The TTS model to use.
            - speaker (optional): The speaker identifier.
            - language (optional): The language code (default is 'de').

        Returns:
            A downloadable audio file (WAV format) on success,
            or a JSON error message with the appropriate HTTP status code.
        """
        Logger.info("POST request received for TTS.")

        json_data = request.get_json()

        if not json_data or 'data' not in json_data:
            Logger.warning("Missing 'data' object in request.")
            return {"error": "Missing data object"}, 400

        data = json_data['data']
        text = data.get('text')
        model = data.get('model')  # Default model
        speaker = data.get('speaker', None)
        language = data.get('language', "de")

        if not text:
            Logger.warning("Missing required 'text' parameter in the request.")
            return {"error": "Missing required 'text' parameter"}, 400

        try:
            Logger.info(
                f"Starting TTS with text='{text[:30]}...' (truncated), model='{model}', speaker='{speaker}', language='{language}'."
            )

            # Ensure all required parameters are passed to synthesize audio.
            audio_buffer = self.tts_service.synthesize_audio(text, model, speaker, language)

            Logger.info("TTS completed successfully. Returning audio file.")
            return send_file(
                audio_buffer,
                mimetype=self.config_manager.get_tts_mimetype(),
                as_attachment=self.config_manager.get_tts_as_attachment(),
                download_name=self.config_manager.get_tts_output_filename()
            )
        except Exception as e:
            Logger.error(f"Internal Server Error: {str(e)}")
            return {"error": f"Internal Server Error: {str(e)}"}, 500
