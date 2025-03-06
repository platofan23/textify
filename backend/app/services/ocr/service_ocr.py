import easyocr
from typing import Literal
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
import torch  # For CUDA check

from backend.app.utils import Logger


def multi_reader(image, model: Literal["easyocr", "doctr"] = "easyocr", language: str = None):
    """
    Perform OCR using the specified model.

    Args:
        image: The image to process.
        model (Literal["easyocr", "doctr"], optional): The OCR model to use. Defaults to "easyocr".
        language (str, optional): The language to use for OCR. Defaults to "en" if not provided.

    Returns:
        str: The recognized text if successful.
        tuple: (Error message, error code) if an error occurs or model is not supported.
    """
    if language is None:
        language = "en"

    try:
        if model == "easyocr":
            Logger.debug(f"Processing image with EasyOCR. Image type: {type(image)}")
            return reader_easyocr(image, [language])
        elif model == "doctr":
            Logger.debug("Processing image with Doctr OCR")
            return reader_doctr(image)
        else:
            Logger.error(f"OCR model '{model}' not supported.")
            return "Model not supported", 404
    except Exception as e:
        Logger.error(f"Error during OCR processing: {str(e)}")
        return f"Internal Server Error: {str(e)}", 500


def reader_easyocr(image, language: list):
    """
    Processes the image using EasyOCR.

    Args:
        image: The image to process.
        language (list): List of languages for OCR.

    Returns:
        str: The extracted text.
    """
    # Consider caching the reader if the language does not change frequently.
    reader = easyocr.Reader(language)
    detections = reader.readtext(image)

    text = " ".join(detection[1] for detection in detections)
    return text


def reader_doctr(image):
    """
    Processes the image using Doctr OCR.

    Args:
        image: The image to process.

    Returns:
        list: A list of text groups with associated average font sizes.

    Raises:
        Exception: Propagates any error encountered during OCR processing.
    """
    try:
        doc = DocumentFile.from_images(image)
        model = ocr_predictor(pretrained=True)
        if torch.cuda.is_available():
            Logger.debug("CUDA is available. Running Doctr OCR on GPU.")
            model = model.cuda()
        result = model(doc)

        text_with_font_size = [
            (word.value, word.geometry[1][1] - word.geometry[0][1], block.geometry)
            for page in result.pages
            for block in page.blocks
            for line in block.lines
            for word in line.words
        ]

        return _font_size_cleanup(text_with_font_size)
    except Exception as e:
        Logger.error(f"Doctr OCR failed: {e}")
        raise


def _font_size_cleanup(text_with_font_size):
    """
    Groups words based on similar font sizes.

    Args:
        text_with_font_size (list): A list of tuples containing word, font size, and geometry.

    Returns:
        list: A list of dictionaries with grouped text and average font size.
    """
    if not text_with_font_size:
        return []

    font_list = []
    size_avg = text_with_font_size[0][1]
    text_list = []
    text_size_list = []

    for index in range(len(text_with_font_size)):
        word, font_size = text_with_font_size[index][0], text_with_font_size[index][1]
        text_size_list.append(font_size)
        size_avg_new = sum(text_size_list) / len(text_size_list)

        if abs(size_avg_new - font_size) > 0.02:
            font_list.append({"text": text_list, "size": size_avg})
            text_list = []
            text_size_list = [font_size]
            size_avg = font_size
            Logger.debug("Font size change detected, grouping text.")
        else:
            size_avg = size_avg_new

        text_list.append(word)

    # Add the last remaining group if any.
    if text_list:
        font_list.append({"text": text_list, "size": size_avg})

    return font_list
