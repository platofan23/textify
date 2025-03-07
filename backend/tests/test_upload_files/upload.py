import requests

# Prepare the file to be uploaded
files = {
    'Files': ('Text_2.png', open('Test_2.png', 'rb'), 'image/png')
}

# Prepare the headers
headers = {
    'User': 'Admin',
    "Title": "Test Title",
}

# Make the POST request
response = requests.post('http://localhost:5558/upload_files', files=files, headers=headers)

# Print the response
print(response.status_code)
print(response.text)

