### tests/test_utils/test_util_pdf_processor.py ###
from unittest.mock import patch, MagicMock
from backend.app.utils import PDFProcessor

def test_pdf_extraction():
    mock_pdf_bytes = b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n%%EOF'
    with patch("fitz.open") as mock_fitz:
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Sample Text"
        mock_fitz.return_value.__enter__.return_value = [mock_page]
        extracted_text = PDFProcessor.extract_text_from_pdf(mock_pdf_bytes)

    assert extracted_text == ["Sample Text"]
