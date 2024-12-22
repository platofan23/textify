import requests


# URL of the Flask route
url = 'http://localhost:5000/login'

# Files to be uploaded
files = [
    ('files', open(r'./test_upload_files/test_apple_wiki.png', 'rb')),
    ('files', open(r'./test_upload_files/test_apple_wiki_infobox.png', 'rb')),
    # Add more files as needed
]

# Send POST request to upload files
response = requests.post(url, files=files, headers={"username": "Chris", "password": "Apple Wiki_4"})

# Print the response from the server
print(response.text)
