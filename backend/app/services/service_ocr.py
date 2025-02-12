import torch
import easyocr

from typing import Literal
from doctr.io import DocumentFile
from doctr.models import ocr_predictor

from backend.app.utils import Logger

DEVICE = torch.device("cuda:0")

def multi_reader(image, model: Literal["easyocr", "doctr"] = "easyocr", language=None):
    if language is None:
        language = "en"

    if model == "easyocr":
        Logger.debug(type(image))
        return reader_easyocr(image, [language])
    elif model == "doctr":
        return reader_doctr(image)
    else:
        return "Model not supported", 404


def reader_easyocr(image, language):
    reader = easyocr.Reader(language)
    detections = reader.readtext(image)

    # Extract the text from the detections
    text = ""
    for detection in detections:
        text += detection[1] + " "
    return text


def reader_doctr(image):
    # Load the image
    doc = DocumentFile.from_images(image)
    # Load the OCR model
    model = ocr_predictor(pretrained=True).to(DEVICE)
    # Perform OCR
    result = model(doc)
    # Extract text and font size
    text_with_font_size = [
        (word.value, word.geometry[1][1] - word.geometry[0][1])
        for page in result.pages
        for block in page.blocks
        for line in block.lines
        for word in line.words
    ]
    text = " ".join(word[0] for word in text_with_font_size)
    font_sizes = [font_size for font_size in _font_size_cleanup(text_with_font_size)]

    return text, font_sizes

def _font_size_cleanup(text_with_font_size):

    font_list = []
    size_avg = text_with_font_size[0][1]
    text_list = []
    text_size_list = []
    for index in range(len(text_with_font_size)):
        font_size = text_with_font_size[index][1]
        text_size_list.append(font_size)

        last_obj_in_list = False

        size_avg_new = (sum(text_size_list)) / len(text_size_list)
        Logger.debug(abs(size_avg_new - font_size))
        Logger.warning(f"F {index}, {len(text_with_font_size)}")

        if abs(size_avg_new - font_size) > 0.015:
            font_list.append({"text": text_list, "size":size_avg})
            text_list = []
            text_size_list = []
            size_avg_new = text_with_font_size[index][1]
            Logger.error(f"Font size cut")
            last_obj_in_list = True

        if index == len(text_with_font_size)-1 and last_obj_in_list:
            font_list.append({"text": text_list, "size":size_avg_new})

        text_list.append(text_with_font_size[index][0])
        size_avg = size_avg_new


    return font_list

