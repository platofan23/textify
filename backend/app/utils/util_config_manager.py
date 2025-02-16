import configparser
import json
import os
import torch
from enum import Enum
from backend.app.utils.util_logger import Logger  # Import the Logger class


class TranslationModel(Enum):
    OPUS_MT = "Helsinki-NLP/opus-mt"
    LIBRE = "LibreTranslate"


class ConfigManager:
    _instance = None  # Singleton instance
    _CONFIG_PATH = './config/docker.ini' if os.getenv("IsDocker") else './config/config.ini'

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):  # Ensure __init__ is only called once
            self.config = configparser.ConfigParser()
            self._load_config()
            self._validate_config()
            self.initialized = True
            Logger.info(f"ConfigManager initialized successfully. Loaded config file: {self._CONFIG_PATH}")

    def _load_config(self):
        if not os.path.exists(self._CONFIG_PATH):
            Logger.error(f"Configuration file not found at: {self._CONFIG_PATH}. Please ensure the file exists.")
            raise FileNotFoundError(f"Configuration file not found at {self._CONFIG_PATH}")
        self.config.read(self._CONFIG_PATH)
        Logger.info(f"Configuration file successfully loaded from: {self._CONFIG_PATH}")

    def _validate_config(self):
        required_sections = ['MONGO_DB', 'REST', 'TRANSLATE', 'TEXT', 'CACHE', 'TTS']
        for section in required_sections:
            if section not in self.config:
                Logger.error(f"Missing required section '{section}' in configuration file. Configuration is invalid.")
                raise ValueError(f"Missing required section '{section}' in configuration file.")

        self._validate_section_keys('TRANSLATE', [
            'HEADER_LIBRE_TRANSLATE', 'MODEL_LIBRE_TRANSLATE', 'MODEL_OPUS_MT', 'TORCH_CPU_DEVICE',
            'TORCH_GPU_DEVICE', 'URL_LIBRE_TRANSLATE', 'OPUS_MODELS_TO_PRELOAD', 'LIBRE_API_KEY'
        ])
        self._validate_section_keys('REST', [
            'ALLOWED_EXTENSIONS', 'HOST', 'MAX_CONTENT_LENGTH_MB', 'MAX_TOTAL_SIZE_GB', 'PORT', 'UPLOAD_FOLDER'
        ])
        self._validate_section_keys('MONGO_DB', [
            'CONNECTION_STRING', 'MONGO_DATABASE', 'MONGO_USERS_COLLECTION', 'MONGO_USER_FILES_COLLECTION'
        ])
        self._validate_section_keys('TEXT', ['MAX_TOKEN'])
        self._validate_section_keys('CACHE', ['MAX_ENTRIES'])
        self._validate_section_keys('TTS', ['AVAILABLE_TTS_MODELS'])
        self._validate_section_keys('TTS', ['AVAILABLE_TTS_SPEAKERS'])

        Logger.info("Configuration validation completed successfully.")

    def _validate_section_keys(self, section: str, required_keys: list):
        for key in required_keys:
            if key not in self.config[section]:
                Logger.error(f"Configuration error: Missing required key '{key}' in section '{section}'.")
                raise ValueError(f"Missing required key '{key}' in section '{section}'.")

    def get_config_value(self, section: str, key: str, value_type: type, default=None):
        try:
            raw_value = self.config.get(section, key, fallback=default)
            if raw_value is None:
                Logger.warning(f"Configuration key '{key}' in section '{section}' not found. Using default: {default}")
                return default
            if value_type == dict:
                return json.loads(raw_value)
            return value_type(raw_value)
        except ValueError as e:
            Logger.error(f"Failed to retrieve configuration value for '{section}.{key}': {str(e)}")
            raise ValueError(f"Failed to retrieve configuration value for '{section}.{key}': {str(e)}")

    def get_torch_device(self) -> str:
        gpu_device = self.config['TRANSLATE']['TORCH_GPU_DEVICE']
        cpu_device = self.config['TRANSLATE']['TORCH_CPU_DEVICE']
        device = gpu_device if torch.cuda.is_available() else cpu_device
        Logger.info(f"Torch device selected: {device} ({'GPU' if torch.cuda.is_available() else 'CPU'})")
        return device

    def get_opus_models_to_preload(self) -> list:
        models = self.config['TRANSLATE']['OPUS_MODELS_TO_PRELOAD']
        Logger.info("Preloading Opus models: " + models)
        return [model.strip() for model in models.split(',') if model.strip()]

    def get_translation_models(self) -> list:
        models = [
            self.config['TRANSLATE']['MODEL_OPUS_MT'],
            self.config['TRANSLATE']['MODEL_LIBRE_TRANSLATE']
        ]
        Logger.info("Retrieved translation model configurations.")
        return models

    def get_mongo_config(self) -> dict:
        config = {
            'connection_string': self.config['MONGO_DB']['CONNECTION_STRING'],
            'database': self.config['MONGO_DB']['MONGO_DATABASE'],
            'users_collection': self.config['MONGO_DB']['MONGO_USERS_COLLECTION'],
            'user_files_collection': self.config['MONGO_DB']['MONGO_USER_FILES_COLLECTION']
        }
        Logger.info("MongoDB configuration successfully retrieved.")
        return config

    def get_tts_models(self) -> list:
        models = self.config['TTS']['AVAILABLE_TTS_MODELS']
        Logger.info("Loaded TTS models: " + models)
        return [model.strip() for model in models.split(',') if model.strip()]

    def get_tts_speakers(self) -> list:
        speakers = self.config['TTS']['AVAILABLE_TTS_SPEAKERS']
        Logger.info("Loaded TTS speakers: " + speakers)
        return [model.strip() for model in speakers.split(',') if speakers.strip()]

    def get_rest_config(self) -> dict:
        config = {
            'host': self.config['REST']['HOST'],
            'port': int(self.config['REST']['PORT']),
            'max_content_length_mb': int(self.config['REST']['MAX_CONTENT_LENGTH_MB']),
            'max_total_size_gb': int(self.config['REST']['MAX_TOTAL_SIZE_GB']),
            'allowed_extensions': self.config['REST']['ALLOWED_EXTENSIONS'].replace(" ", "").split(','),
            'upload_folder': self.config['REST']['UPLOAD_FOLDER']
        }
        Logger.info("REST API configuration successfully retrieved.")
        return config
