import torch
import easyocr

from typing import Literal
from doctr.io import DocumentFile
from doctr.models import ocr_predictor

DEVICE = torch.device("cuda:0")

def multi_reader(image, model: Literal["easyocr", "doctr"] = "easyocr", language=None):
    if language is None:
        language = "en"

    if model == "easyocr":
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
    # Extract text
    text = " ".join(
        word.value
        for page in result.pages
        for block in page.blocks
        for line in block.lines
        for word in line.words
    )
    return text
