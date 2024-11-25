import easyocr
from typing import Literal


def multi_reader(image, model: Literal["easyocr"] = "easyocr", language=None):
    if language is None:
        language = 'en'

    if model == "easyocr":

        return reader_easyocr(image, [language])
    else:
        raise ValueError('Model not supported')

def reader_easyocr(image, language):
    reader = easyocr.Reader(language)
    detections = reader.readtext(image)


    # Extract the text from the detections
    text = ""
    for detection in detections:
        text += detection[1] + " "
    return text


