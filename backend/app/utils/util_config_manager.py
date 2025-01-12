import configparser
import json
import os
import torch
from enum import Enum


class TranslationModel(Enum):
    OPUS_MT = "Helsinki-NLP/opus-mt"
    LIBRE = "LibreTranslate"


class ConfigManager:
    _instance = None  # Singleton instance
    DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), './config/config.ini')

    def __init__(self, config_path: str = None):
        self.config = configparser.ConfigParser()
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.load_config()
        self.validate_config()

    def load_config(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found at {self.config_path}")
        self.config.read(self.config_path)

    def validate_config(self):
        required_sections = ['MONGO_DB', 'REST', 'TRANSLATE', 'TEXT', 'CACHE']
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing '{section}' section in config file.")

        # Validate keys for TRANSLATE section
        translate_required_keys = [
            'HEADER_LIBRE_TRANSLATE',
            'MODEL_LIBRE_TRANSLATE',
            'MODEL_OPUS_MT',
            'TORCH_CPU_DEVICE',
            'TORCH_GPU_DEVICE',
            'URL_LIBRE_TRANSLATE',
            'OPUS_MODELS_TO_PRELOAD',
            'LIBRE_API_KEY'
        ]
        for key in translate_required_keys:
            if key not in self.config['TRANSLATE']:
                raise ValueError(f"Missing required key '{key}' in 'TRANSLATE' section.")

        # Validate keys for REST section
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

        # Validate keys for MONGO_DB section
        mongo_required_keys = ['CONNECTION_STRING', 'MONGO_DATABASE', 'MONGO_USERS_COLLECTION']
        for key in mongo_required_keys:
            if key not in self.config['MONGO_DB']:
                raise ValueError(f"Missing required key '{key}' in 'MONGO_DB' section.")

        # Validate keys for TEXT section
        if 'MAX_TOKEN' not in self.config['TEXT']:
            raise ValueError("Missing required key 'MAX_TOKEN' in 'TEXT' section.")

        # Validate keys for CACHE section
        if 'MAX_ENTRIES' not in self.config['CACHE']:
            raise ValueError("Missing required key 'MAX_ENTRIES' in 'CACHE' section.")

    def get_torch_device(self) -> str:
        gpu_device = self.config['TRANSLATE']['TORCH_GPU_DEVICE']
        cpu_device = self.config['TRANSLATE']['TORCH_CPU_DEVICE']
        return gpu_device if torch.cuda.is_available() else cpu_device

    def get_opus_models_to_preload(self) -> list:
        models = self.config['TRANSLATE']['OPUS_MODELS_TO_PRELOAD']
        return [model.strip() for model in models.split(',') if model.strip()]

    def get_mongo_config(self) -> dict:
        return {
            'connection_string': self.config['MONGO_DB']['CONNECTION_STRING'],
            'database': self.config['MONGO_DB']['MONGO_DATABASE'],
            'users_collection': self.config['MONGO_DB']['MONGO_USERS_COLLECTION']
        }

    def get_rest_config(self) -> dict:
        return {
            'host': self.config['REST']['HOST'],
            'port': int(self.config['REST']['PORT']),
            'max_content_length_mb': int(self.config['REST']['MAX_CONTENT_LENGTH_MB']),
            'allowed_extensions': self.config['REST']['ALLOWED_EXTENSIONS'].split(','),
            'upload_folder': self.config['REST']['UPLOAD_FOLDER']
        }

    def get_libre_translate_config(self) -> dict:
        headers = self.config['TRANSLATE']['HEADER_LIBRE_TRANSLATE']
        return {
            'url': self.config['TRANSLATE']['URL_LIBRE_TRANSLATE'],
            'headers': json.loads(headers)
        }

    def get_model_names(self) -> dict:
        return {
            'opus_mt': self.config['TRANSLATE']['MODEL_OPUS_MT'],
            'libre_translate': self.config['TRANSLATE']['MODEL_LIBRE_TRANSLATE']
        }

    def get_libre_api_key(self) -> str:
        return self.config['TRANSLATE']['LIBRE_API_KEY']

    def get_text_config(self) -> dict:
        """
        Retrieves the configuration for text processing.

        Returns:
            dict: A dictionary containing max token settings.
        """
        return {
            'max_token': int(self.config['TEXT']['MAX_TOKEN'])
        }

    def get_cache_config(self) -> dict:
        """
        Retrieves the configuration for cache management.

        Returns:
            dict: A dictionary containing cache settings.
        """
        return {
            'max_entries': int(self.config['CACHE']['MAX_ENTRIES'])
        }

    def get_config_value(self, section: str, key: str, value_type: type, default=None):
        try:
            raw_value = self.config.get(section, key, fallback=default)
            if raw_value is None:
                return default
            if value_type == dict:
                return json.loads(raw_value)
            return value_type(raw_value)
        except ValueError as e:
            raise ValueError(f"Error retrieving config value for {section}.{key}: {str(e)}")
