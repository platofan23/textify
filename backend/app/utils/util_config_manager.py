import configparser
import json
import os
import torch

from enum import Enum

class TranslationModel(Enum):
    _instance = None  # Singleton instance
    """
    TranslationModel defines the available translation models.

    This enumeration is used to ensure that only valid models are selected
    for the translation process.

    Attributes:
        OPUS_MT (str): Represents the OpusMT translation model.
        LIBRE (str): Represents the LibreTranslate API.
    """
    OPUS_MT = "Helsinki-NLP/opus-mt"
    LIBRE = "LibreTranslate"

class ConfigManager:
    """
    ConfigManager handles the loading, validation, and retrieval of configuration
    values from a configuration file.

    This class ensures that only the necessary configuration parameters
    from the provided config.ini are loaded and accessed.
    """

    _instance = None  # Singleton instance

    DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../config/config.ini')

    def __init__(self, config_path: str = None):
        """
        Initializes the ConfigManager and loads the configuration from the specified file
        or a default path if no path is provided.

        Args:
            config_path (str, optional): Path to the configuration file. Defaults to None.

        Raises:
            FileNotFoundError: If the configuration file does not exist.
        """
        self.config = configparser.ConfigParser()
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.load_config()
        self.validate_config()

    def load_config(self):
        """
        Loads the configuration from the specified file path.

        Raises:
            FileNotFoundError: If the configuration file does not exist.
        """
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found at {self.config_path}")

        self.config.read(self.config_path)

    def validate_config(self):
        """
        Validates that the necessary configuration sections and keys exist.

        Raises:
            ValueError: If the required configuration section or key is missing.
        """
        required_sections = ['MONGO_DB', 'REST', 'TRANSLATE']
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing '{section}' section in config file.")

        translate_required_keys = [
            'HEADER_LIBRE_TRANSLATE',
            'MODEL_LIBRE_TRANSLATE',
            'MODEL_OPUS_MT',
            'TORCH_CPU_DEVICE',
            'TORCH_GPU_DEVICE',
            'URL_LIBRE_TRANSLATE',
            'OPUS_MODELS_TO_PRELOAD'
        ]
        for key in translate_required_keys:
            if key not in self.config['TRANSLATE']:
                raise ValueError(f"Missing required key '{key}' in 'TRANSLATE' section.")

        rest_required_keys = [
            'ALLOWED_EXTENSIONS',
            'HOST',
            'MAX_CONTENT_LENGTH_MB',
            'PORT',
            'UPLOAD_FOLDER'
        ]
        for key in rest_required_keys:
            if key not in self.config['REST']:
                raise ValueError(f"Missing required key '{key}' in 'REST' section.")

        mongo_required_keys = ['CONNECTION_STRING', 'MONGO_DATABASE', 'MONGO_USERS_COLLECTION']
        for key in mongo_required_keys:
            if key not in self.config['MONGO_DB']:
                raise ValueError(f"Missing required key '{key}' in 'MONGO_DB' section.")

    def get_torch_device(self) -> str:
        """
        Determines the appropriate Torch device (GPU or CPU) for model execution.

        Returns:
            str: The GPU device if available, otherwise the CPU device.
        """
        gpu_device = self.config['TRANSLATE']['TORCH_GPU_DEVICE']
        cpu_device = self.config['TRANSLATE']['TORCH_CPU_DEVICE']
        return gpu_device if torch.cuda.is_available() else cpu_device

    def get_opus_models_to_preload(self) -> list:
        """
        Retrieves the list of OpusMT models to preload.

        Returns:
            list: A list of model pairs (e.g., ['en-de', 'en-fr']).
        """
        models = self.config['TRANSLATE']['OPUS_MODELS_TO_PRELOAD']
        return [model.strip() for model in models.split(',') if model.strip()]

    def get_mongo_config(self) -> dict:
        """
        Retrieves MongoDB-related configuration.

        Returns:
            dict: A dictionary containing MongoDB settings.
        """
        return {
            'connection_string': self.config['MONGO_DB']['CONNECTION_STRING'],
            'database': self.config['MONGO_DB']['MONGO_DATABASE'],
            'users_collection': self.config['MONGO_DB']['MONGO_USERS_COLLECTION']
        }

    def get_rest_config(self) -> dict:
        """
        Retrieves REST API configuration.

        Returns:
            dict: A dictionary containing REST settings.
        """
        return {
            'host': self.config['REST']['HOST'],
            'port': int(self.config['REST']['PORT']),
            'max_content_length_mb': int(self.config['REST']['MAX_CONTENT_LENGTH_MB']),
            'allowed_extensions': self.config['REST']['ALLOWED_EXTENSIONS'].split(','),
            'upload_folder': self.config['REST']['UPLOAD_FOLDER']
        }

    def get_libre_translate_config(self) -> dict:
        """
        Retrieves LibreTranslate API configuration.

        Returns:
            dict: A dictionary containing LibreTranslate API settings.
        """
        headers = self.config['TRANSLATE']['HEADER_LIBRE_TRANSLATE']
        return {
            'url': self.config['TRANSLATE']['URL_LIBRE_TRANSLATE'],
            'headers': json.loads(headers)
        }

    def get_model_names(self) -> dict:
        """
        Retrieves translation model names.

        Returns:
            dict: A dictionary containing model names for OpusMT and LibreTranslate.
        """
        return {
            'opus_mt': self.config['TRANSLATE']['MODEL_OPUS_MT'],
            'libre_translate': self.config['TRANSLATE']['MODEL_LIBRE_TRANSLATE']
        }

    def get_config_value(self, section: str, key: str, value_type: type, default=None):
        """
        Retrieves a configuration value from a specific section.

        Args:
            section (str): The section in the config file.
            key (str): The key to retrieve.
            value_type (type): The expected type of the value (e.g., int, str).
            default: The default value to return if the key does not exist.

        Returns:
            The value from the configuration file, cast to the specified type, or the default value.
        """
        try:
            raw_value = self.config.get(section, key, fallback=default)
            if raw_value is None:
                return default
            if value_type == dict:
                return json.loads(raw_value)
            return value_type(raw_value)
        except ValueError as e:
            raise ValueError(f"Error retrieving config value for {section}.{key}: {str(e)}")
