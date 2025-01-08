import configparser
import json
import os
import torch

from enum import Enum


class TranslationModel(Enum):
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

    This class abstracts configuration logic, ensuring that necessary parameters
    are correctly loaded and accessible throughout the application.
    """

    DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../config/config.ini')

    def __init__(self, config_path: str = None):
        """
        Initializes the ConfigManager and loads the configuration from the specified file
        or a default path if no path is provided.

        Args:
            config_path (str, optional): Path to the configuration file. Defaults to None.

        Raises:
            ValueError: If the required configuration sections or keys are missing.
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
        if 'TRANSLATE' not in self.config:
            raise ValueError("Missing 'TRANSLATE' section in config file.")

        required_keys = ['TORCH_GPU_DEVICE', 'TORCH_CPU_DEVICE',
                         'URL_LIBRE_TRANSLATE', 'HEADER_LIBRE_TRANSLATE']

        for key in required_keys:
            if key not in self.config['TRANSLATE']:
                raise ValueError(f"Missing required key '{key}' in 'TRANSLATE' section.")

    def get_torch_device(self) -> str:
        """
        Determines the appropriate Torch device (GPU or CPU) for model execution.

        Returns:
            str: The GPU device if available, otherwise the CPU device.
        """
        gpu_device = self.config['TRANSLATE']['TORCH_GPU_DEVICE']
        cpu_device = self.config['TRANSLATE']['TORCH_CPU_DEVICE']
        return gpu_device if torch.cuda.is_available() else cpu_device

    def get_libre_translate_url(self) -> str:
        """
        Retrieves the LibreTranslate API URL from the configuration.

        Returns:
            str: The API URL for LibreTranslate.
        """
        return self.config['TRANSLATE']['URL_LIBRE_TRANSLATE']

    def get_libre_translate_headers(self) -> dict:
        """
        Retrieves the headers required for LibreTranslate API requests.

        Returns:
            dict: Headers required for LibreTranslate requests.

        Raises:
            json.JSONDecodeError: If the headers are not in valid JSON format.
            ValueError: If header parsing fails.
        """
        try:
            headers = self.config['TRANSLATE']['HEADER_LIBRE_TRANSLATE']
            return json.loads(headers)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format in 'HEADER_LIBRE_TRANSLATE' configuration.")
