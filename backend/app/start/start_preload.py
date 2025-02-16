import torch
from transformers import MarianMTModel, MarianTokenizer
from TTS.api import TTS
from backend.app.utils.util_logger import Logger  # Import the Logger class

def preload_models(config_manager, cache_manager):
    """
    Preloads specified OpusMT models and multiple TTS models synchronously.

    Args:
        config_manager (ConfigManager): Configuration manager for loading settings.
        cache_manager (CacheManager): Cache manager for storing preloaded models and tokenizers.
    """
    Logger.info("🔄 [Preloading] Starting to preload OpusMT and TTS models...")

    # Load OpusMT models
    models_to_preload = config_manager.get_config_value('TRANSLATE', 'OPUS_MODELS_TO_PRELOAD', str, default="").split(',')
    device = config_manager.get_torch_device()

    for model_pair in models_to_preload:
        model_key = model_pair.strip()
        model_name = f"Helsinki-NLP/opus-mt-{model_key}"

        if cache_manager.get(f"model-{model_key}") is not None and cache_manager.get(f"tokenizer-{model_key}") is not None:
            Logger.info(f"✅ [OpusMT] Model '{model_name}' already preloaded and cached.")
            continue

        try:
            Logger.info(f"🔍 [OpusMT] Loading model '{model_name}'...")
            tokenizer = MarianTokenizer.from_pretrained(model_name)
            model = MarianMTModel.from_pretrained(model_name)
            model.to(torch.device(device))

            cache_manager.set(f"model-{model_key}", model)
            cache_manager.set(f"tokenizer-{model_key}", tokenizer)
            Logger.info(f"✅ [OpusMT] Successfully preloaded and cached '{model_name}'.")
        except Exception as e:
            Logger.error(f"❌ [OpusMT] Failed to preload model '{model_name}': {str(e)}")

    # Load multiple TTS models
    tts_models_to_preload = config_manager.get_config_value('TTS', 'AVAILABLE_TTS_MODELS', str, default="").split(',')

    for tts_model_name in tts_models_to_preload:
        tts_model_name = tts_model_name.strip()

        if cache_manager.get(f"tts_model-{tts_model_name}") is not None:
            Logger.info(f"✅ [TTS] Model '{tts_model_name}' already preloaded and cached.")
            continue

        try:
            Logger.info(f"🔍 [TTS] Loading TTS model '{tts_model_name}'...")
            tts_model = TTS(model_name=tts_model_name)
            tts_model.to(device)

            # Store only in RAM (not persistent)
            cache_manager.set(f"tts_model-{tts_model_name}", tts_model)
            Logger.info(f"✅ [TTS] Successfully preloaded and cached TTS model '{tts_model_name}' on {device}.")
        except Exception as e:
            Logger.error(f"❌ [TTS] Failed to preload TTS model '{tts_model_name}': {str(e)}")

    Logger.info("✅ [Preloading] All models have been successfully preloaded.")
