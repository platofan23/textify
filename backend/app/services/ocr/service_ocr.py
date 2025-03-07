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

        text_blocks = []
        for page in result.pages:
            for block in page.blocks:
                # Collect words and sizes in format for _font_size_cleanup
                words_with_sizes = [
                    (word.value, word.geometry[1][1] - word.geometry[0][1])
                    for line in block.lines 
                    for word in line.words
                ]
                
                # Process the words with font size grouping
                processed_data = _font_size_cleanup(words_with_sizes)
                
                block_data = {
                    "Block": {
                        "Data": processed_data,
                        "Block_Geometry": block.geometry
                    }
                }
                text_blocks.append(block_data)

        Logger.debug(f"OCR result: {text_blocks}")
        Logger.debug(f"Extracted text: {extract_text_from_ocr_result(text_blocks)}")
        return text_blocks
    except Exception as e:
        Logger.error(f"Doctr OCR failed: {e}")
        raise


def extract_text_from_ocr_result(ocr_result):
    """
    Extracts all text from the OCR result JSON structure.
    
    Args:
        ocr_result: List of text blocks returned by reader_doctr
        
    Returns:
        str: All extracted text combined into a single string
    """
    all_text = []
    
    for block in ocr_result:
        for text_group in block["Block"]["Data"]:
            all_text.extend(text_group["text"])
    
    return " ".join(all_text)


# TODO: Implement translation
def update_ocr_text(ocr_result, target_language):
    """
    Updates text in the OCR result by translating it to the target language.

    Args:
        ocr_result: List of text blocks returned by reader_doctr
        target_language: Language code to translate the text into

    Returns:
        List: Updated OCR result structure
    """
    translator = Translator()
    updated_result = []

    for block in ocr_result:
        updated_block = {"Block": {"Block_Geometry": block["Block"]["Block_Geometry"], "Data": []}}

        for text_group in block["Block"]["Data"]:
            # Translate each word in the text list
            translated_text = [translator.translate(word, dest=target_language).text for word in text_group["text"]]

            # Create updated text group with the same size
            updated_text_group = {
                "text": translated_text,
                "size": text_group["size"]
            }

            updated_block["Block"]["Data"].append(updated_text_group)

        updated_result.append(updated_block)

    return updated_result


def _font_size_cleanup(text_with_font_size: list, threshold: float = None) -> list:
    """
    Groups text by similar font sizes to identify structural elements in the document.
    
    Args:
        text_with_font_size: List of tuples containing (word, font_size)
        threshold: Size difference threshold to consider a new font group.
                   If None, a dynamic threshold will be calculated.
        
    Returns:
        List of dictionaries with grouped text and their average font sizes
    """
    if not text_with_font_size:
        return []
        
    # Calculate dynamic threshold if not explicitly provided
    if threshold is None:
        font_sizes = [size for _, size in text_with_font_size]
        if font_sizes:
            size_range = max(font_sizes) - min(font_sizes)
            Logger.debug(f"Font size range: {size_range:.6f}")
            # Use 30% of the range for small ranges, 15% for larger ranges
            if size_range < 0.08:  # Define small range threshold
                threshold = max(0.005, size_range * 0.3)
                Logger.debug(f"Using 30% dynamic threshold for small range: {threshold:.6f}")
            else:
                threshold = max(0.005, size_range * 0.15)
                Logger.debug(f"Using 15% dynamic threshold for larger range: {threshold:.6f}")
        else:
            threshold = 0.02
    
    font_groups = []
    current_words = []
    current_sizes = []
    
    for word, font_size in text_with_font_size:
        # Calculate new running average if we have sizes
        if current_sizes:
            current_sizes.append(font_size)
            size_avg_new = sum(current_sizes) / len(current_sizes)
            
            # Check if significant font size change detected
            if abs(size_avg_new - font_size) > threshold:
                # Store the current group
                font_groups.append({"text": current_words, "size": sum(current_sizes[:-1]) / len(current_sizes[:-1])})
                Logger.debug(f"Font size change detected: {font_size:.4f}")
                
                # Start new group with current word
                current_words = [word]
                current_sizes = [font_size]
                continue
        else:
            # First word in document
            current_sizes = [font_size]
            
        current_words.append(word)

    # Add the last group
    if current_words:
        font_groups.append({"text": current_words, "size": sum(current_sizes) / len(current_sizes)})

    return font_groups
