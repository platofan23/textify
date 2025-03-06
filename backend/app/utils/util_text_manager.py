from typing import Union, List
from itertools import chain
from backend.app.utils.util_logger import Logger  # Import the Logger class

def preprocess_text(text: Union[str, List[str]]) -> str:
    """
    Preprocesses text by converting lists of strings into a single string.

    Args:
        text (Union[str, List[str]]): Text to preprocess, either as a string or a list of strings.

    Returns:
        str: A single concatenated string if a list is provided, otherwise the original string.
    """
    if isinstance(text, list):
        Logger.debug("Preprocessing text: Joining list of strings into a single string.")
        return ' '.join(text)
    Logger.debug("Preprocessing text: Returning original string.")
    return text

def split_text_into_chunks(tokenizer, text: str, max_tokens: int = 150) -> List[str]:
    """
    Splits text into smaller chunks based on a specified maximum token limit.

    Args:
        tokenizer: The tokenizer used to tokenize and detokenize text.
        text (str): The input text to be split.
        max_tokens (int): The maximum number of tokens per chunk (default: 150).

    Returns:
        List[str]: A list of text chunks, each within the specified token limit.

    Raises:
        ValueError: If the input text is empty or tokenization fails.
    """
    if not text:
        Logger.error("Input text is empty. Cannot split into chunks.")
        raise ValueError("Input text cannot be empty.")

    tokens = tokenizer.tokenize(text)
    if not tokens:
        Logger.error("Tokenization failed or produced empty tokens.")
        raise ValueError("Tokenization failed or produced empty tokens.")

    Logger.info(f"Splitting text into chunks with max token limit: {max_tokens}.")
    return [
        tokenizer.convert_tokens_to_string(tokens[i:i + max_tokens])
        for i in range(0, len(tokens), max_tokens)
    ]

def flatten_list(nested_list: List) -> List[str]:
    """
    Flattens a nested list into a single list of strings.

    Args:
        nested_list (List): A list that may contain nested lists.

    Returns:
        List[str]: A flat list of strings.
    """
    Logger.debug("Flattening nested list.")
    return list(chain.from_iterable(
        [str(item)] if not isinstance(item, list) else [str(sub_item) for sub_item in item if sub_item]
        for item in nested_list
    ))

def join_and_split_translations(translated_chunks: List[str], split_into_sentences: bool = False) -> List[str]:
    """
    Joins translated text chunks into a single string and optionally splits it into individual sentences.

    Args:
        translated_chunks (List[str]): List of translated text chunks.
        split_into_sentences (bool): Whether to split the joined text into sentences.

    Returns:
        List[str]: A list containing either the full translated text as a single element or individual sentences.
    """
    Logger.info("Joining and optionally splitting translated text.")

    # Flatten nested chunks and filter out empty items.
    flat_chunks = flatten_list(translated_chunks)
    if not flat_chunks:
        Logger.warning("No text available to join or split.")
        return []  # Return an empty list if no text is available

    # Join the flat list into a single string.
    translated_text = ' '.join(flat_chunks)

    if split_into_sentences:
        Logger.info("Splitting joined text into sentences.")
        sentences = []
        current_sentence = []
        for token in translated_text.split():
            current_sentence.append(token)
            if token.endswith(('.', '!', '?')):
                sentences.append(' '.join(current_sentence))
                current_sentence = []
        if current_sentence:
            sentences.append(' '.join(current_sentence))
        return sentences

    return [translated_text]
