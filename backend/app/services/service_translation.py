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

# Load configuration from file
config = configparser.ConfigParser()
config.read('../config/config.ini')

# Cache for translated sentences
translation_cache = LRUCache(maxsize=1000)

class Model(Enum):
    """
    Enum for model selection between OpusMT and LibreTranslate.
    """
    Opus = config['TRANSLATE']['MODEL_OPUS_MT']
    Libre = config['TRANSLATE']['MODEL_LIBRE_TRANSLATE']

@lru_cache(maxsize=3)
def load_model_and_tokenizer(model_name):
    """
    Loads and caches the MarianMT model and tokenizer.
    """
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)
    return tokenizer, model

def split_text_into_chunks(tokenizer, text, max_tokens=100):
    """
    Splits the input text into chunks of a maximum number of tokens.

    Args:
        tokenizer: The tokenizer used to count tokens.
        text (str): The text to split.
        max_tokens (int): Maximum number of tokens per chunk.

    Returns:
        list: List of text chunks.
    """
    tokens = tokenizer.tokenize(text)
    chunks = []
    for i in range(0, len(tokens), max_tokens):
        chunk_tokens = tokens[i:i + max_tokens]
        chunk_text = tokenizer.convert_tokens_to_string(chunk_tokens)
        chunks.append(chunk_text)
    return chunks

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
        translated_pages = []

        # Process each page
        for page in pdf_document:
            page_text = page.get_text()
            translated_text = translate_text(model, sourcelanguage, targetlanguage, page_text)
            translated_pages.append(translated_text)

        pdf_document.close()
        return translated_pages

    except Exception as e:
        return {"error": f"Failed to extract PDF text: {str(e)}"}

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
        return translate_opusmt(sourcelanguage, targetlanguage, text, isFile=False)
    elif model == Model.Libre.value:
        return translate_libre(sourcelanguage, targetlanguage, text)
    else:
        return None

def translate_opusmt(sourcelanguage, targetlanguage, text, isFile=False):
    """
    Übersetzt Text mit dem OpusMT-Modell von Helsinki-NLP.
    Unterstützt Caching und Geräteeinstellung zur Optimierung.

    Args:
        sourcelanguage (str): Source language code.
        targetlanguage (str): Target language code.
        text (str): Text to translate.
        isFile (bool): Indicates if the text is part of a file.

    Returns:
        list: List of translated sentences.
    """
    if isinstance(text, list):
        text = ' '.join(text)  # Konvertieren Sie Listen in Strings

    # Inkludiere den Modellnamen im Cache-Key, um Konflikte zu vermeiden
    cache_key = f"Opus-{sourcelanguage}-{targetlanguage}-{text}"
    if cache_key in translation_cache:
        return translation_cache[cache_key]

    model_name = f"Helsinki-NLP/opus-mt-{sourcelanguage}-{targetlanguage}"
    device = config['TRANSLATE']['TORCH_GPU_DEVICE'] if torch.cuda.is_available() else config['TRANSLATE']['TORCH_CPU_DEVICE']

    tokenizer, model = load_model_and_tokenizer(model_name)
    model.to(torch.device(device))

    # Text in Chunks mit max 100 Tokens aufteilen
    chunks = split_text_into_chunks(tokenizer, text, max_tokens=100)
    translated_chunks = []

    for chunk in chunks:
        inputs = tokenizer(chunk, return_tensors="pt", padding=True, truncation=True, max_length=100).to(torch.device(device))
        with torch.amp.autocast(device_type=device):
            translated = model.generate(**inputs)

        outputs = tokenizer.batch_decode(translated, skip_special_tokens=True)
        translated_chunks.extend(outputs)

    # Optional: Übersetzte Chunks zu einem einzelnen Text zusammenfügen
    translated_text = ' '.join(translated_chunks)
    sentences = re.split(r'(?<=[.!?]) +', translated_text) if isFile else translated_chunks

    # Ergebnis cachen
    translation_cache[cache_key] = sentences
    return sentences

def translate_libre(sourcelanguage, targetlanguage, text):
    """
    Übersetzt Text mit der LibreTranslate API.

    Args:
        sourcelanguage (str): Source language code.
        targetlanguage (str): Target language code.
        text (str): Text to translate.

    Returns:
        list: List of translated sentences.
    """
    if isinstance(text, list):
        text = ' '.join(text)  # Konvertieren Sie Listen in Strings

    # Da LibreTranslate kein direktes Tokenizer-Interface bietet, verwenden wir den MarianTokenizer, um Chunks zu erstellen
    # Dies dient nur der Bestimmung der Tokenanzahl und zur Chunk-Aufteilung
    tokenizer = MarianTokenizer.from_pretrained(f"Helsinki-NLP/opus-mt-{sourcelanguage}-{targetlanguage}")
    chunks = split_text_into_chunks(tokenizer, text, max_tokens=100)
    translated_chunks = []

    url = config['TRANSLATE']['URL_LIBRE_TRANSLATE']
    headers = json.loads(config['TRANSLATE']['HEADER_LIBRE_TRANSLATE'])

    for chunk in chunks:
        # Inkludiere den Modellnamen im Cache-Key, um Konflikte zu vermeiden
        cache_key = f"Libre-{sourcelanguage}-{targetlanguage}-{chunk}"
        if cache_key in translation_cache:
            translated_text = translation_cache[cache_key]
        else:
            payload = {
                "q": chunk,
                "source": sourcelanguage,
                "target": targetlanguage,
                "format": "text"
            }

            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                result = response.json()
                translated_text = result.get("translatedText", chunk)
                # Cache das Ergebnis
                translation_cache[cache_key] = translated_text
            else:
                # Fehlerbehandlung oder den Original-Chunk beibehalten
                translated_text = chunk

        translated_chunks.append(translated_text)

    # Optional: Übersetzte Chunks zu einem einzelnen Text zusammenfügen
    translated_text = ' '.join(translated_chunks)
    return re.split(r'(?<=[.!?]) +', translated_text)
