import unittest
import logging
from unittest.mock import patch, MagicMock
import requests

# Configure logging to capture DEBUG messages (plus warnings and errors).
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class FileUploadTestCase(unittest.TestCase):
    @patch('requests.post')
    def test_file_upload_success(self, mock_post):
        """
        Test for a successful file upload. This test simulates a scenario where
        the server returns a 200 response with a success message.
        """
        logger.debug("Starting test_file_upload_success.")

        # Simulate a successful response from the server.
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = 'Files uploaded successfully'
        mock_post.return_value = mock_response
        logger.debug("Mocked requests.post to return 200 and success message.")

        # Prepare the files to be uploaded as a list of tuples.
        files = [
            ('files', ('test_apple_wiki.png', b'testdata1', 'image/png')),
            ('files', ('test_apple_wiki_infobox.png', b'testdata2', 'image/png')),
        ]
        logger.debug("Prepared file upload data: %s", files)

        # Make the simulated POST request.
        response = requests.post('http://localhost:5555/register', files=files,
                                 headers={"username": "Admin", "password": "123"})
        logger.debug("Received response: status_code=%s, text='%s'", response.status_code, response.text)

        # Assertions: Check if the response status and text match the expected values.
        self.assertEqual(response.status_code, 200, "Expected a 200 response status for success.")
        self.assertEqual(response.text, 'Files uploaded successfully', "Expected success message not received.")
        logger.debug("test_file_upload_success passed.")

    @patch('requests.post')
    def test_file_upload_failure(self, mock_post):
        """
        Test for a failure in file upload. This test simulates a scenario where
        the server returns a 500 error with an appropriate error message.
        """
        logger.debug("Starting test_file_upload_failure.")

        # Simulate a failure response from the server.
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = 'Error uploading files'
        mock_post.return_value = mock_response
        logger.debug("Mocked requests.post to return 500 and error message.")

        # Prepare a file to be uploaded.
        files = [
            ('files', ('test_apple_wiki.png', b'testdata1', 'image/png')),
        ]
        logger.debug("Prepared file upload data: %s", files)

        # Make the simulated POST request.
        response = requests.post('http://localhost:5555/register', files=files,
                                 headers={"username": "Admin", "password": "123"})
        logger.debug("Received response: status_code=%s, text='%s'", response.status_code, response.text)

        # Assertions: Check if the response status and text match the expected error values.
        self.assertEqual(response.status_code, 500, "Expected a 500 response status for failure.")
        self.assertEqual(response.text, 'Error uploading files', "Expected error message not received.")
        logger.debug("test_file_upload_failure passed.")


if __name__ == '__main__':
    # Start method: Run the tests if this file is executed directly.
    unittest.main()