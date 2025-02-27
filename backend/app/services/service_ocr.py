import easyocr
from typing import Literal
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
import torch  # Import torch for CUDA check

from backend.app.utils import Logger


def multi_reader(image, model: Literal["easyocr", "doctr"] = "easyocr", language=None):
    if language is None:
        language = "en"

    try:
        if model == "easyocr":
            Logger.debug(type(image))
            return reader_easyocr(image, [language])
        elif model == "doctr":
            return reader_doctr(image)
        else:
            return "Model not supported", 404
    except Exception as e:
        Logger.error(f"Error during OCR processing: {str(e)}")
        return f"Internal Server Error: {str(e)}", 500


def reader_easyocr(image, language):
    # Consider caching readers if language doesn't change often
    reader = easyocr.Reader(language)
    detections = reader.readtext(image)

    text = " ".join(detection[1] for detection in detections)
    return text


def reader_doctr(image):
    try:
        doc = DocumentFile.from_images(image)
        model = ocr_predictor(pretrained=True)
        if torch.cuda.is_available():
            Logger.debug("CUDA is available")
            model = model.cuda()
        result = model(doc)

        text_with_font_size = [
            (word.value, word.geometry[1][1] - word.geometry[0][1])
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
    if not text_with_font_size:
        return []

    font_list = []
    size_avg = text_with_font_size[0][1]
    text_list = []
    text_size_list = []

    for index in range(len(text_with_font_size)):
        word, font_size = text_with_font_size[index]
        text_size_list.append(font_size)
        size_avg_new = sum(text_size_list) / len(text_size_list)


        if abs(size_avg_new - font_size) > 0.02:
            font_list.append({"text": text_list, "size": size_avg})
            text_list = []
            text_size_list = [font_size]
            size_avg = font_size
            Logger.debug("Font size cut detected")
        else:
            size_avg = size_avg_new

        text_list.append(word)

    # Add the last remaining group
    if text_list:
        font_list.append({"text": text_list, "size": size_avg})

    return font_list
