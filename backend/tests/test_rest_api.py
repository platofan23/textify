import unittest
from unittest.mock import patch, MagicMock
import requests


class FileUploadTestCase(unittest.TestCase):
    @patch('requests.post')
    def test_file_upload_success(self, mock_post):
        # Simulate successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = 'Files uploaded successfully'
        mock_post.return_value = mock_response

        # Prepare files
        files = [
            ('files', ('test_apple_wiki.png', b'testdata1', 'image/png')),
            ('files', ('test_apple_wiki_infobox.png', b'testdata2', 'image/png')),
        ]

        response = requests.post('http://localhost:5555/register', files=files,
                                 headers={"username": "Admin", "password": "123"})

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, 'Files uploaded successfully')

    @patch('requests.post')
    def test_file_upload_failure(self, mock_post):
        # Simulate failure response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = 'Error uploading files'
        mock_post.return_value = mock_response

        files = [
            ('files', ('test_apple_wiki.png', b'testdata1', 'image/png')),
        ]

        response = requests.post('http://localhost:5555/register', files=files,
                                 headers={"username": "Admin", "password": "123"})

        # Assertions
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.text, 'Error uploading files')


if __name__ == '__main__':
    unittest.main()
