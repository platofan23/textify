import easyocr
from parso.python.tree import Class

class Ocr:
    def __init__(self, model=easyocr, languages=None):
        if languages is None:
            languages = ['en']

        if model is easyocr:
            self.reader = easyocr.Reader(languages)
        else:
            raise ValueError('Model not supported')

    def read_text(self, image):
        detections = self.reader.readtext(image)
        # Extract the text from the detections
        text = ""
        for detection in detections:
            text += detection[1]
        return text
