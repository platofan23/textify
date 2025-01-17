import torch
from transformers import MarianMTModel, MarianTokenizer
from backend.app.utils.util_logger import Logger  # Importiere die Logger-Klasse

def preload_models(config_manager, cache_manager):
    """
    Preloads specified OpusMT models synchronously.

    Args:
        config_manager (ConfigManager): Configuration manager for loading settings.
        cache_manager (CacheManager): Cache manager for storing preloaded models and tokenizers.
    """
    Logger.info("🔄 Preloading OpusMT models...")
    models_to_preload = config_manager.get_config_value('TRANSLATE', 'OPUS_MODELS_TO_PRELOAD', str, default="").split(',')

    device = config_manager.get_torch_device()

    for model_pair in models_to_preload:
        model_name = f"Helsinki-NLP/opus-mt-{model_pair.strip()}"
        try:
            tokenizer = MarianTokenizer.from_pretrained(model_name)
            model = MarianMTModel.from_pretrained(model_name)
            model.to(torch.device(device))

            cache_manager.set(f"model-{model_pair.strip()}", model)
            cache_manager.set(f"tokenizer-{model_pair.strip()}", tokenizer)
            Logger.info(f"✅ {model_name} successfully preloaded and cached.")
        except Exception as e:
            Logger.error(f"❌ Failed to preload model {model_name}: {str(e)}")
