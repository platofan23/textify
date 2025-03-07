import fitz
from typing import List
from backend.app.utils.util_logger import Logger  # Import the Logger class

class PDFProcessor:
    """
    Handles the extraction of text from PDF files using PyMuPDF (fitz).

    This class provides a simple interface for extracting text from multi-page PDFs,
    enabling further processing such as translation. It handles errors gracefully.
    """
    _instance = None  # Singleton instance (if needed in future extensions)

    @staticmethod
    def extract_text_from_pdf(file_content: bytes) -> List[str]:
        """
        Extracts text from each page of a PDF file.

        Args:
            file_content (bytes): The binary content of the PDF file.

        Returns:
            List[str]: A list of strings, each representing the text extracted from a single PDF page.

        Raises:
            RuntimeError: If text extraction fails due to invalid data or other errors.
        """
        try:
            Logger.info("Starting text extraction from PDF.")
            with fitz.open("pdf", file_content) as pdf_document:
                extracted_text = [page.get_text() for page in pdf_document]
                Logger.info(f"Successfully extracted text from {len(extracted_text)} page(s).")
                return extracted_text
        except fitz.FileDataError as e:
            Logger.error(f"Failed to process PDF due to invalid data: {str(e)}")
            raise RuntimeError(f"Failed to process PDF: {str(e)}")
        except Exception as e:
            Logger.error(f"Unexpected error during PDF extraction: {str(e)}")
            raise RuntimeError(f"Unexpected error during PDF extraction: {str(e)}")
