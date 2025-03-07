import unittest
import logging
from unittest.mock import patch, MagicMock, call

from backend.app.utils import PDFProcessor

# Configure logging for this module to capture DEBUG, WARNING, and ERROR messages.
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def test_pdf_extraction():
    """
    Test the PDF extraction functionality of PDFProcessor.extract_text_from_pdf.

    This test simulates the behavior of fitz.open by patching it so that the PDF file
    is represented by a mocked page that returns a fixed string ("Sample Text")
    when its get_text() method is called.
    """
    # Arrange: Prepare a sample PDF byte stream.
    mock_pdf_bytes = b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n%%EOF'
    logger.debug("Starting PDF extraction test with sample PDF bytes.")

    # Patch the 'fitz.open' function which is used internally in PDFProcessor.
    with patch("fitz.open") as mock_fitz:
        # Create a mock page with a defined behavior.
        mock_page = MagicMock()
        # When get_text() is called on the mock page, it returns "Sample Text".
        mock_page.get_text.return_value = "Sample Text"
        logger.debug("Mock page configured to return 'Sample Text' when get_text() is called.")

        # Setup the mocked context manager. When fitz.open() is used in a with-statement,
        # its __enter__() method returns a list containing our mock_page.
        mock_fitz.return_value.__enter__.return_value = [mock_page]

        # Act: Call the function under test to extract text from the PDF bytes.
        extracted_text = PDFProcessor.extract_text_from_pdf(mock_pdf_bytes)
        logger.debug("Extracted text from PDF: %s", extracted_text)

    # Assert: Verify that the extracted text matches the expected result.
    assert extracted_text == ["Sample Text"], "The extracted text did not match the expected output."
    # (No info-level logging is used per requirements; only debug and warnings/errors will be output.)