import re

from typing import Union, List


def preprocess_text(text: Union[str, List[str]]) -> str:
    """
    Preprocesses text by converting lists of strings into a single string.

    This function is useful when dealing with extracted text in chunks,
    ensuring that lists of text fragments are combined for further processing.

    Args:
        text (Union[str, List[str]]): Text to preprocess, either as a string or a list of strings.

    Returns:
        str: A single concatenated string if a list is provided, otherwise the original string.
    """
    return ' '.join(text) if isinstance(text, list) else text


def split_text_into_chunks(tokenizer, text: str, max_tokens: int = 100) -> List[str]:
    """
    Splits text into smaller chunks based on a specified maximum token limit.

    This function uses a tokenizer to ensure that the text is split into
    chunks that fit within the maximum number of tokens, preventing overflow
    during translation model input.

    Args:
        tokenizer: The tokenizer used to tokenize and detokenize text.
        text (str): The input text to be split.
        max_tokens (int): The maximum number of tokens per chunk (default: 100).

    Returns:
        List[str]: A list of text chunks, each within the specified token limit.

    Raises:
        ValueError: If the input text is empty or the tokenizer fails to tokenize.
    """
    if not text:
        raise ValueError("Input text cannot be empty.")

    tokens = tokenizer.tokenize(text)
    if not tokens:
        raise ValueError("Tokenization failed or produced empty tokens.")

    return [
        tokenizer.convert_tokens_to_string(tokens[i:i + max_tokens])
        for i in range(0, len(tokens), max_tokens)
    ]


def flatten_list(nested_list: List) -> List[str]:
    """
    Flattens a list of lists into a single list.

    Args:
        nested_list (List): A list that may contain nested lists.

    Returns:
        List[str]: A flat list of strings.

    Notes:
        This function filters out empty entries during the flattening process.
    """
    flattened = []
    for item in nested_list:
        if isinstance(item, list):
            flattened.extend([str(i) for i in item if i])  # Convert and filter empty entries
        elif item:
            flattened.append(str(item))
    return flattened


def join_and_split_translations(translated_chunks: List[str], split_into_sentences: bool = False) -> List[str]:
    """
    Joins and optionally splits translated text into individual sentences.

    This function combines translated chunks and splits them into sentences based
    on punctuation. It can return either full text or split sentences.

    Args:
        translated_chunks (List[str]): List of translated text chunks.
        split_into_sentences (bool): Whether to split the joined text into sentences.

    Returns:
        List[str]: List of sentences or full translated text depending on the split flag.
    """
    # Flatten list of chunks
    flat_chunks = flatten_list(translated_chunks)

    if not flat_chunks:
        return []  # Return empty list if no text is available

    # Join list into a single string
    translated_text = ' '.join(flat_chunks)

    # Optionally split the text by sentence
    return re.split(r'(?<=[.!?]) +', translated_text) if split_into_sentences else [translated_text]
