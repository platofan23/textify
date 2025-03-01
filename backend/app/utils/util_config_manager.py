import configparser
import json
import os
import torch
from backend.app.utils.util_logger import Logger  # Import the Logger class

class ConfigManager:
    _instance = None  # Singleton instance
    _CONFIG_PATH = './config/docker.ini' if os.getenv("IsDocker") else './config/config.ini'

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):  # Ensure __init__ runs only once
            self.config = configparser.ConfigParser()
            self._config_cache = {}  # Cache for configuration values
            self._load_config()
            self._validate_config()
            self._initialized = True
            Logger.info(f"ConfigManager initialized successfully. Loaded config file: {self._CONFIG_PATH}")

    def _load_config(self):
        """Loads the configuration file from disk."""
        if not os.path.exists(self._CONFIG_PATH):
            Logger.error(f"Configuration file not found at: {self._CONFIG_PATH}.")
            raise FileNotFoundError(f"Configuration file not found at {self._CONFIG_PATH}")
        self.config.read(self._CONFIG_PATH)
        Logger.info(f"Configuration file loaded from: {self._CONFIG_PATH}")

    def _validate_config(self):
        """Validates that all required sections and keys are present in the configuration."""
        required_sections = ['MONGO_DB', 'REST', 'TRANSLATE', 'TEXT', 'CACHE', 'TTS', 'DEVICE']
        for section in required_sections:
            if section not in self.config:
                Logger.error(f"Missing required section '{section}' in configuration file.")
                raise ValueError(f"Missing required section '{section}' in configuration file.")
        # Validate required keys in each section
        self._validate_section_keys('CACHE', ['MAX_ENTRIES'])
        self._validate_section_keys('DEVICE', ['TORCH_CPU_DEVICE', 'TORCH_GPU_DEVICE'])
        self._validate_section_keys('MONGO_DB', [
            'CONNECTION_STRING', 'MONGO_DATABASE', 'MONGO_USERS_COLLECTION', 'MONGO_USER_FILES_COLLECTION'
        ])
        self._validate_section_keys('REST', [
            'ALLOWED_EXTENSIONS', 'HOST', 'MAX_CONTENT_LENGTH_MB', 'MAX_TOTAL_SIZE_GB', 'PORT', 'UPLOAD_FOLDER'
        ])
        self._validate_section_keys('TEXT', ['MAX_TOKEN'])
        self._validate_section_keys('TRANSLATE', ['AVAILABLE_MODELS'])
        self._validate_section_keys('TTS', ['AVAILABLE_MODELS', 'AVAILABLE_SPEAKERS', 'AVAILABLE_LANGUAGES'])
        Logger.info("Configuration validation completed successfully.")

    def _validate_section_keys(self, section: str, required_keys: list):
        """Ensures that all keys in `required_keys` exist in the given section."""
        for key in required_keys:
            if key not in self.config[section]:
                Logger.error(f"Missing required key '{key}' in section '{section}'.")
                raise ValueError(f"Missing required key '{key}' in section '{section}'.")

    def get_config_value(self, section: str, key: str, value_type: type, default=None):
        """
        Retrieves a configuration value, using a cache to prevent duplicate lookups.

        Args:
            section (str): The configuration section.
            key (str): The key within the section.
            value_type (type): The expected type of the value.
            default: A default value if the key is not found.
        Returns:
            The configuration value converted to the specified type.
        """
        cache_key = f"{section}.{key}"
        if cache_key in self._config_cache:
            return self._config_cache[cache_key]
        try:
            raw_value = self.config.get(section, key, fallback=default)
            if raw_value is None:
                Logger.warning(f"Configuration key '{key}' in section '{section}' not found. Using default: {default}")
                value = default
            elif value_type == dict:
                value = json.loads(raw_value)
            else:
                value = value_type(raw_value)
            self._config_cache[cache_key] = value
            Logger.info(f"Configuration value for '{cache_key}' loaded: {value}")
            return value
        except Exception as e:
            Logger.error(f"Failed to retrieve config value '{section}.{key}': {str(e)}")
            raise ValueError(f"Failed to retrieve configuration value for '{section}.{key}': {str(e)}")

    def get_torch_device(self) -> str:
        """
        Returns the appropriate torch device based on CUDA availability and config settings.
        """
        gpu_device = self.get_config_value('DEVICE', 'TORCH_GPU_DEVICE', str)
        cpu_device = self.get_config_value('DEVICE', 'TORCH_CPU_DEVICE', str)
        device = gpu_device if torch.cuda.is_available() else cpu_device
        Logger.info(f"Torch device selected: {device} ({'GPU' if torch.cuda.is_available() else 'CPU'})")
        return device

    def get_rest_config(self) -> dict:
        """
        Returns REST API configuration as a dictionary.
        """
        config = {
            'host': self.get_config_value('REST', 'HOST', str),
            'port': self.get_config_value('REST', 'PORT', int),
            'max_content_length_mb': self.get_config_value('REST', 'MAX_CONTENT_LENGTH_MB', int),
            'max_total_size_gb': self.get_config_value('REST', 'MAX_TOTAL_SIZE_GB', int),
            'allowed_extensions': self.get_config_value('REST', 'ALLOWED_EXTENSIONS', str).replace(" ", "").split(','),
            'upload_folder': self.get_config_value('REST', 'UPLOAD_FOLDER', str)
        }
        Logger.info("REST API configuration retrieved.")
        return config

    def get_mongo_config(self) -> dict:
        """
        Returns MongoDB configuration as a dictionary.
        """
        config = {
            'connection_string': self.get_config_value('MONGO_DB', 'CONNECTION_STRING', str),
            'database': self.get_config_value('MONGO_DB', 'MONGO_DATABASE', str),
            'users_collection': self.get_config_value('MONGO_DB', 'MONGO_USERS_COLLECTION', str),
            'user_files_collection': self.get_config_value('MONGO_DB', 'MONGO_USER_FILES_COLLECTION', str)
        }
        Logger.info("MongoDB configuration retrieved.")
        return config

    def get_translation_models(self) -> list:
        """
        Returns a list of available translation model names.
        """
        models = self.get_config_value('TRANSLATE', 'AVAILABLE_MODELS', str)
        Logger.info("Translation models retrieved.")
        return [model.strip() for model in models.split(',') if model.strip()]

    def get_tts_models(self) -> list:
        """
        Returns a list of available TTS model names.
        """
        models = self.get_config_value('TTS', 'AVAILABLE_MODELS', str)
        Logger.info("TTS models retrieved: " + models)
        return [models.strip() for models in models.split(',') if models.strip()]

    def get_tts_languages(self) -> list:
        """
        Returns a list of available TTS languages.
        """
        languages = self.get_config_value('TTS', 'AVAILABLE_LANGUAGES', str)
        Logger.info("TTS languages retrieved: " + languages)
        return [languages.strip() for languages in languages.split(',') if languages.strip()]

    def get_tts_speakers(self) -> list:
        """
        Returns a list of available TTS speakers.
        """
        speakers = self.get_config_value('TTS', 'AVAILABLE_SPEAKERS', str)
        Logger.info("TTS speakers retrieved: " + speakers)
        return [speakers.strip() for speakers in speakers.split(',') if speakers.strip()]
