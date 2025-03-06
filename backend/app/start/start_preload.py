import torch
from transformers import MarianMTModel, MarianTokenizer
from TTS.api import TTS
from backend.app.utils.util_logger import Logger  # Import the Logger class


def _preload_translation_model(model_name: str, device: str, cache_manager):
    """
    Helper function to preload an OpusMT translation model and its tokenizer.

    Args:
        model_name (str): Full model name (e.g., "Helsinki-NLP/opus-mt-en-de").
        device (str): Torch device (e.g., "cpu" or "cuda").
        cache_manager: Instance of CacheManager to store preloaded models.
    """
    model_key = model_name.strip()
    if cache_manager.get(f"model-{model_key}") is not None and \
       cache_manager.get(f"tokenizer-{model_key}") is not None:
        Logger.info(f"[OpusMT] Model '{model_name}' is already preloaded and cached.")
        return

    try:
        Logger.info(f"[OpusMT] Loading model '{model_name}'...")
        tokenizer = MarianTokenizer.from_pretrained(model_name)
        model = MarianMTModel.from_pretrained(model_name)
        model.to(torch.device(device))
        cache_manager.set(f"model-{model_key}", model)
        cache_manager.set(f"tokenizer-{model_key}", tokenizer)
        Logger.info(f"[OpusMT] Successfully preloaded and cached '{model_name}'.")
    except Exception as e:
        Logger.error(f"[OpusMT] Failed to preload model '{model_name}': {str(e)}")


def _preload_tts_model(tts_model_name: str, device: str, cache_manager):
    """
    Helper function to preload a TTS model and keep it in memory.

    Args:
        tts_model_name (str): Full TTS model name.
        device (str): Torch device (e.g., "cpu" or "cuda").
        cache_manager: Instance of CacheManager for storing preloaded TTS models.
    """
    tts_model_name = tts_model_name.strip()

    try:
        Logger.info(f"[Preloading] Loading TTS model '{tts_model_name}' into RAM...")
        tts_model = TTS(tts_model_name)
        tts_model.to(device)

        # Store model in memory cache.
        cache_manager.cache_tts_model(tts_model_name, tts_model)

        # Verify that the model was successfully cached.
        if cache_manager.load_cached_tts_model(tts_model_name):
            Logger.info(f"[Preloading] Successfully cached TTS model '{tts_model_name}' in RAM.")
        else:
            Logger.error(f"[Preloading] Failed to cache TTS model '{tts_model_name}' in RAM!")
    except Exception as e:
        Logger.error(f"[Preloading] Failed to preload TTS model '{tts_model_name}': {str(e)}")


def preload_models(config_manager, cache_manager):
    """
    Preloads specified OpusMT translation models and TTS models synchronously.

    Args:
        config_manager (ConfigManager): Provides configuration settings.
        cache_manager (CacheManager): Manages caching of preloaded models and tokenizers.
    """
    Logger.info("[Preloading] Starting to preload OpusMT and TTS models...")
    device = config_manager.get_torch_device()

    # Preload translation models using the configured translation models list.
    models_to_preload = config_manager.get_translation_models()  # Returns list of model names.
    for model_name in models_to_preload:
        _preload_translation_model(model_name, device, cache_manager)

    # Preload TTS models using the configured TTS models list.
    tts_models_to_preload = config_manager.get_tts_models()
    for tts_model_name in tts_models_to_preload:
        _preload_tts_model(tts_model_name, device, cache_manager)
