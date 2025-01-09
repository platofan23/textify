import fitz  # PyMuPDF
from typing import List


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
            fitz.FileDataError: If the file is not a valid PDF.
            fitz.FileNotFoundError: If the PDF file cannot be opened.
            RuntimeError: If text extraction fails for an unknown reason.
        """
        try:
            with fitz.open("pdf", file_content) as pdf_document:
                return [page.get_text() for page in pdf_document]
        except fitz.FileDataError as e:
            raise RuntimeError(f"Failed to process PDF: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error during PDF extraction: {str(e)}")
