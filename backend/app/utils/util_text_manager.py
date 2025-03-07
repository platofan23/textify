from itertools import chain

import re
import unicodedata
from typing import Union, List
from backend.app.utils.util_logger import Logger


def preprocess_text(text: Union[str, List[str]]) -> str:
    """
    Preprocesses the input text by normalizing Unicode characters, removing extra whitespace,
    filtering out excessive special characters, and converting a list of strings to a single string if needed.

    Enhancements:
    - Joins a list of strings into a single string.
    - Normalizes Unicode characters (e.g., converts accented characters).
    - Removes extra whitespace and collapses multiple spaces.
    - Replaces multiple dots (`..`) with an ellipsis (`...`).
    - Collapses repeated punctuation marks (`!!!` → `!`).
    - Filters out sequences of random special characters (`#$%&*!@` → `*` if it’s meaningful).

    Args:
        text (Union[str, List[str]]): The raw input text.

    Returns:
        str: A cleaned and normalized string.
    """

    if isinstance(text, list):
        Logger.info("Preprocessing: Joining list of strings.")
        text = ' '.join(text)

    # Normalize Unicode (e.g., combining accented characters)
    text = unicodedata.normalize('NFKC', text)

    # Remove excessive whitespace
    text = ' '.join(text.split())

    # Replace multiple dots with an ellipsis
    text = re.sub(r'\.{2,}', '...', text)

    # Collapse repeated punctuation (e.g., "!!!" -> "!")
    text = re.sub(r'([!?.,;:])\1+', r'\1', text)

    # Remove excessive non-alphanumeric special characters (e.g., "$#@!%" → "!")
    text = re.sub(r'[^a-zA-Z0-9\s.,!?;:()-]+', '', text)

    Logger.info("Preprocessing: Completed normalization and special character cleanup.")
    return text

def split_text_into_chunks(tokenizer, text: str, max_tokens: int = 250) -> List[str]:
    """
    Splits the preprocessed text into chunks that do not exceed the specified token limit.
    The splitting is done in a sentence-aware manner so that sentences are not arbitrarily cut.

    Args:
        tokenizer: A tokenizer with 'tokenize' and 'convert_tokens_to_string' methods.
        text (str): The input text to be split.
        max_tokens (int): Maximum number of tokens per chunk (default is 150).

    Returns:
        List[str]: A list of text chunks.
    """
    if not text:
        Logger.error("Input text is empty; cannot split into chunks.")
        raise ValueError("Input text cannot be empty.")

    # Preprocess the text first
    text = preprocess_text(text)

    # Split text into sentences (split on punctuation followed by whitespace)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    Logger.info(f"Split text into {len(sentences)} sentences.")
    chunks = []
    current_chunk = []
    current_token_count = 0

    for sentence in sentences:
        tokens = tokenizer.tokenize(sentence)
        num_tokens = len(tokens)
        # If a sentence exceeds the token limit, add it as its own chunk.
        if num_tokens > max_tokens:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_token_count = 0
            chunks.append(sentence)
            continue

        if current_token_count + num_tokens > max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentence]
            current_token_count = num_tokens
        else:
            current_chunk.append(sentence)
            current_token_count += num_tokens

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    Logger.info(f"Text split into {len(chunks)} chunks (max {max_tokens} tokens each).")
    return chunks

def flatten_list(nested_list: List) -> List[str]:
    """
    Flattens a nested list into a single list of strings.

    Args:
        nested_list (List): A list that may contain nested lists.

    Returns:
        List[str]: A flat list of strings.
    """
    Logger.info("Flattening nested list.")
    return list(chain.from_iterable(
        [str(item)] if not isinstance(item, list) else [str(sub_item) for sub_item in item if sub_item]
        for item in nested_list
    ))

def join_and_split_translations(translated_chunks: List[str], split_into_sentences: bool = False) -> List[str]:
    """
    Joins a list of translated text chunks into a single string and optionally splits it into sentences.

    Args:
        translated_chunks (List[str]): List of translated text chunks.
        split_into_sentences (bool): Whether to split the joined text into sentences.

    Returns:
        List[str]: Either a list containing the full joined text or a list of sentences.
    """
    Logger.info("Joining translated text chunks.")
    flat_chunks = flatten_list(translated_chunks)
    if not flat_chunks:
        Logger.warning("No text available to join.")
        return []
    joined_text = " ".join(flat_chunks)
    if split_into_sentences:
        Logger.info("Splitting joined text into sentences.")
        sentences = re.split(r'(?<=[.!?])\s+', joined_text)
        return sentences
    return [joined_text]

def clean_translated_text(text: str) -> str:
    """
    Cleans the translated text by removing duplicate punctuation and extraneous characters.

    Args:
        text (str): The translated text.

    Returns:
        str: The cleaned text.
    """
    # Replace multiple dots with an ellipsis.
    text = re.sub(r'\.{2,}', '...', text)
    # Collapse repeated punctuation.
    text = re.sub(r'([!?,;:])\1+', r'\1', text)
    # Normalize whitespace.
    text = " ".join(text.split())
    Logger.info("Cleaned translated text.")
    return text