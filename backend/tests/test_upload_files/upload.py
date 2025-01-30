import requests

# Prepare the file to be uploaded
files = {
    'File': ('test_apple_wiki.png', open('test_apple_wiki.png', 'rb'), 'image/png')
}

# Prepare the headers
headers = {
    'User': 'Admin',
    "Title": "Test Title",
}

# Make the POST request
response = requests.post('http://localhost:5555/upload_files', files=files, headers=headers)

# Print the response
print(response.status_code)
print(response.text)

