import base64

import configparser
import fitz
import json
import requests
from functools import lru_cache
from cachetools import LRUCache
from enum import Enum
from transformers import MarianMTModel, MarianTokenizer
import torch
import re

# Load Config
config = configparser.ConfigParser()
config.read('../config/config.ini')

# Translate PDF file
def translate_file(file, model, sourcelanguage, targetlanguage):
    """
    Decodes a base64-encoded PDF file, extracts the text from each page,
    and translates the content page by page.

    Args:
        file (str): Base64-encoded PDF file.
        model (str): Translation model (OpusMT or LibreTranslate).
        sourcelanguage (str): Source language code.
        targetlanguage (str): Target language code.

    Returns:
        list: A list containing the translated text for each page.
    """
    try:
        # Decode the base64-encoded file
        file_content = base64.b64decode(file)

        # Open the PDF file
        pdf_document = fitz.open("pdf", file_content)

        # Translate each page and store the results in a list
        translated_pages = []
        for page in pdf_document:
            page_text = page.get_text()

            # Translate the entire page
            translated_text = translate_text(model, sourcelanguage, targetlanguage, page_text)
            translated_pages.append(translated_text)

        pdf_document.close()

        # Return the list of translated pages
        return translated_pages

    except Exception as e:
        # Return an error if something goes wrong
        return {"error": f"Failed to extract PDF text: {str(e)}"},


# Translate text using OpusMT or LibreTranslate
def translate_text(model, sourcelanguage, targetlanguage, text):
    """
    Translates text using the specified translation model (OpusMT or LibreTranslate).

    Args:
        model (str): Translation model to use.
        sourcelanguage (str): Source language code.
        targetlanguage (str): Target language code.
        text (str): Text to translate.

    Returns:
        list: List of translated sentences.
    """
    if model == Model.Opus.value:
        return translate_opusmt(sourcelanguage,targetlanguage,text, False)
    elif model == Model.Libre.value:
        return translate_libre(sourcelanguage,targetlanguage,text)
    else:
        return None


# Cache for translated sentences
translation_cache = LRUCache(maxsize=1000)


# Caching model and tokenizer loading
@lru_cache(maxsize=3)
def load_model_and_tokenizer(model_name):
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)
    return tokenizer, model


# Translation function
def translate_opusmt(sourcelanguage, targetlanguage, text, isFile=False):
    cache_key = f"{sourcelanguage}-{targetlanguage}-{text}"
    if cache_key in translation_cache:
        return translation_cache[cache_key]

    model_name = f"Helsinki-NLP/opus-mt-{sourcelanguage}-{targetlanguage}"
    device = torch.device(config['TRANSLATE']['TORCH_GPU_DEVICE'] if torch.cuda.is_available() else config['TRANSLATE'][
        'TORCH_CPU_DEVICE'])

    tokenizer, model = load_model_and_tokenizer(model_name)
    model.to(device)

    # Prepare input text
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True).to(device)

    # Mixed precision for faster inference
    with torch.amp.autocast(config['TRANSLATE']['TORCH_GPU_DEVICE']):
        translated = model.generate(**inputs)

    outputs = tokenizer.batch_decode(translated, skip_special_tokens=True)

    # If translating a file, split sentences
    if isFile:
        sentences = re.split(r'(?<=[.!?]) +', outputs[0])
    else:
        sentences = outputs

    translation_cache[cache_key] = sentences
    return sentences


# Translate using LibreTranslate (Single request per page)
def translate_libre(sourcelanguage, targetlanguage, text):
    """
    Translates text using LibreTranslate API.

    Args:
        sourcelanguage (str): Source language code.
        targetlanguage (str): Target language code.
        text (str): Text to translate.

    Returns:
        list: List of translated sentences.
    """
    url = config['TRANSLATE']['URL_LIBRE_TRANSLATE']
    headers = json.loads(config['TRANSLATE']['HEADER_LIBRE_TRANSLATE'])
    payload = {
        "q": text,
        "source": sourcelanguage,
        "target": targetlanguage,
        "format": "text"
    }

    # Send translation request to LibreTranslate API
    response = requests.post(url, headers=headers, json=payload)
    result = response.json()

    # Split the translated text into sentences
    translated_text = result.get("translatedText", text)
    sentences = re.split(r'(?<=[.!?]) +', translated_text)
    return sentences


# Enum for model selection
class Model(Enum):
    Opus = config['TRANSLATE']['MODEL_OPUS_MT']
    Libre = config['TRANSLATE']['MODEL_LIBRE_TRANSLATE']
