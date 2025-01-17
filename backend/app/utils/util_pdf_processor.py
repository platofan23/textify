import fitz
from typing import List
from backend.app.utils.util_logger import Logger  # Importiere die Logger-Klasse

class PDFProcessor:
    """
    PDFProcessor handles the extraction of text from PDF files.

    This class uses PyMuPDF (fitz) to read and extract text from PDF documents,
    facilitating further processing such as translation.

    Benefits:
    - Provides a simple interface for text extraction from PDFs.
    - Supports multi-page PDFs by extracting text page by page.
    - Handles potential errors gracefully during PDF processing.
    """

    _instance = None  # Singleton instance

    @staticmethod
    def extract_text_from_pdf(file_content: bytes) -> List[str]:
        """
        Extracts text from each page of a PDF file.

        Args:
            file_content (bytes): The binary content of the PDF file.

        Returns:
            List[str]: A list of strings, where each entry represents the text
                      extracted from a single PDF page.

        Raises:
            RuntimeError: If text extraction fails for any reason.
        """
        try:
            Logger.info("Starting text extraction from PDF.")
            with fitz.open("pdf", file_content) as pdf_document:
                extracted_text = [page.get_text() for page in pdf_document]
                Logger.info(f"Successfully extracted text from {len(extracted_text)} pages.")
                return extracted_text
        except fitz.FileDataError as e:
            Logger.error(f"Failed to process PDF due to invalid data: {str(e)}")
            raise RuntimeError(f"Failed to process PDF: {str(e)}")
        except Exception as e:
            Logger.error(f"Unexpected error during PDF extraction: {str(e)}")
            raise RuntimeError(f"Unexpected error during PDF extraction: {str(e)}")
