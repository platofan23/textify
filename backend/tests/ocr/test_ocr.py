import unittest
from unittest.mock import patch, MagicMock, call
import numpy as np
import torch

# Import the functions to test from parent directory
from backend.app.services.ocr.service_ocr import (
    multi_reader,
    reader_easyocr,
    reader_doctr,
    extract_text_from_ocr_result,
    _font_size_cleanup
)

class TestOCRService(unittest.TestCase):
    
    def setUp(self):
        # Sample test image as numpy array (1x1 black pixel)
        self.test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        
    @patch('easyocr.Reader')
    def test_reader_easyocr(self, mock_reader):
        # Setup mock
        mock_instance = mock_reader.return_value
        mock_instance.readtext.return_value = [
            ([[0, 0], [10, 0], [10, 10], [0, 10]], "Hello", 0.9),
            ([[20, 0], [40, 0], [40, 10], [20, 10]], "World", 0.8)
        ]
        
        # Call function
        result = reader_easyocr(self.test_image, ["en"])
        
        # Assertions
        mock_reader.assert_called_once_with(["en"])
        mock_instance.readtext.assert_called_once_with(self.test_image)
        self.assertEqual(result, "Hello World")
    
    @patch('torch.cuda.is_available', return_value=False)
    @patch('backend.app.services.ocr.service_ocr.ocr_predictor')
    @patch('backend.app.services.ocr.service_ocr.DocumentFile')
    @patch('backend.app.services.ocr.service_ocr._font_size_cleanup')
    @patch('backend.app.services.ocr.service_ocr.Logger')
    def test_reader_doctr(self, mock_logger, mock_cleanup, mock_doc_file, mock_predictor, mock_cuda):
        # Create mock document and predictor
        mock_doc = MagicMock()
        mock_doc_file.from_images.return_value = mock_doc
        
        # Create mock model and result
        mock_model = MagicMock()
        mock_predictor.return_value = mock_model
        
        # Create mock page with blocks, lines and words
        mock_word = MagicMock()
        mock_word.value = "test"
        mock_word.geometry = [[0, 0], [0.1, 0.05]]  # [[x0,y0], [x1,y1]]
        
        mock_line = MagicMock()
        mock_line.words = [mock_word]
        
        mock_block = MagicMock()
        mock_block.lines = [mock_line]
        mock_block.geometry = [[0, 0], [0.1, 0.05]]
        
        mock_page = MagicMock()
        mock_page.blocks = [mock_block]
        
        mock_result = MagicMock()
        mock_result.pages = [mock_page]
        
        mock_model.return_value = mock_result
        
        # Mock font size cleanup function
        mock_cleanup.return_value = [{"text": ["test"], "size": 0.05}]
        
        # Call function
        result = reader_doctr(self.test_image)
        
        # Assertions
        mock_doc_file.from_images.assert_called_once_with(self.test_image)
        mock_predictor.assert_called_once_with(pretrained=True)
        mock_model.assert_called_once_with(mock_doc)
        mock_cleanup.assert_called_once()
        
        # Check result format
        self.assertEqual(len(result), 1)  # One block
        self.assertIn("Block", result[0])
        self.assertIn("Data", result[0]["Block"])
        self.assertIn("Block_Geometry", result[0]["Block"])

    @patch('backend.app.services.ocr.service_ocr.reader_easyocr')
    @patch('backend.app.services.ocr.service_ocr.reader_doctr')
    @patch('backend.app.services.ocr.service_ocr.Logger')
    def test_multi_reader_easyocr(self, mock_logger, mock_doctr, mock_easyocr):
        mock_easyocr.return_value = "Hello World"
        
        result = multi_reader(self.test_image, model="easyocr")
        
        mock_easyocr.assert_called_once_with(self.test_image, ["en"])
        mock_doctr.assert_not_called()
        self.assertEqual(result, "Hello World")

    @patch('backend.app.services.ocr.service_ocr.reader_easyocr')
    @patch('backend.app.services.ocr.service_ocr.reader_doctr')  
    @patch('backend.app.services.ocr.service_ocr.Logger')
    def test_multi_reader_doctr(self, mock_logger, mock_doctr, mock_easyocr):
        mock_doctr.return_value = [{"Block": {"Data": [{"text": ["Hello"], "size": 0.05}]}}]
        
        result = multi_reader(self.test_image, model="doctr")
        
        mock_doctr.assert_called_once_with(self.test_image)
        mock_easyocr.assert_not_called()
        self.assertEqual(result, [{"Block": {"Data": [{"text": ["Hello"], "size": 0.05}]}}])

    @patch('backend.app.services.ocr.service_ocr.Logger')
    def test_multi_reader_unsupported_model(self, mock_logger):
        result = multi_reader(self.test_image, model="unsupported_model")
        
        self.assertEqual(result, ("Model not supported", 404))
        mock_logger.error.assert_called_once()

    @patch('backend.app.services.ocr.service_ocr.reader_easyocr')
    @patch('backend.app.services.ocr.service_ocr.Logger')
    def test_multi_reader_exception(self, mock_logger, mock_easyocr):
        mock_easyocr.side_effect = Exception("Test error")
        
        result = multi_reader(self.test_image)
        
        self.assertEqual(result, ("Internal Server Error: Test error", 500))
        mock_logger.error.assert_called_once()

    def test_extract_text_from_ocr_result(self):
        ocr_result = [
            {
                "Block": {
                    "Data": [
                        {"text": ["Hello", "world"], "size": 0.05},
                        {"text": ["Another", "block"], "size": 0.03}
                    ],
                    "Block_Geometry": [[0, 0], [0.1, 0.05]]
                }
            },
            {
                "Block": {
                    "Data": [
                        {"text": ["Second", "part"], "size": 0.04}
                    ],
                    "Block_Geometry": [[0.2, 0.2], [0.3, 0.25]]
                }
            }
        ]
        
        result = extract_text_from_ocr_result(ocr_result)
        
        self.assertEqual(result, "Hello world Another block Second part")

    def test_font_size_cleanup_empty(self):
        result = _font_size_cleanup([])
        self.assertEqual(result, [])

    def test_font_size_cleanup_single_group(self):
        text_with_sizes = [
            ("Hello", 0.05),
            ("World", 0.05),
            ("Test", 0.05)
        ]
        
        result = _font_size_cleanup(text_with_sizes)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["text"], ["Hello", "World", "Test"])
        self.assertEqual(round(result[0]["size"], 2), 0.05)


if __name__ == '__main__':
    unittest.main()