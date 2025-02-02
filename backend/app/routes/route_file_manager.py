import json

from Cryptodome.Cipher import AES
from Cryptodome.Hash import SHA256
from Cryptodome.Protocol.KDF import HKDF
from Cryptodome.PublicKey import ECC
from Cryptodome.Random import get_random_bytes
from PIL import Image
import io

from flask import send_file
from flask_restful import Resource, reqparse
from werkzeug.datastructures import FileStorage
from backend.app.utils import Logger, MongoDBManager, ConfigManager

# Load configuration
config_manager = ConfigManager()

MAX_TOTAL_SIZE = int(config_manager.get_rest_config().get("max_total_size_gb")) * 1024 * 1024 * 1024
ALLOWED_EXTENSIONS = set(config_manager.get_rest_config().get("allowed_extensions"))

# MongoDB setup
mongo_manager = MongoDBManager()

# Helper function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Resource for file upload
class UploadFile(Resource):
    def post(self):
        # Validate parameters
        parser = reqparse.RequestParser()
        parser.add_argument('User', location='headers', required=True, help="User header is required")
        parser.add_argument('Title', location='headers', required=True, help="Title header is required")
        parser.add_argument('File', type=FileStorage, location="files", action='append', required=True)
        args = parser.parse_args()

        files = args['File']
        username = args['User']
        title = args['Title']

        total_size = 0
        file_ids = []

        # check if user exists
        user = mongo_manager.find_documents(config_manager.get_mongo_config().get("users_collection"), {'Username': username})[0]
        if not user:
            Logger.error('User not found')
            return {'error': 'User not found'}, 404

        # Save files to MongoDB
        for file in files:
            if file.filename == '':
                Logger.error('No selected file')
                return {'error': 'No selected file'}, 400
            if allowed_file(file.filename):
                total_size += len(file.read())
                file.seek(0)
                if total_size > MAX_TOTAL_SIZE:
                    # Reverse changes by deleting uploaded files
                    for file_id in file_ids:
                        mongo_manager.delete_documents(config_manager.get_mongo_config().get("user_files_collection"), {'_id': file_id}, use_GridFS=False)
                    Logger.error(f'Total file size exceeds {MAX_TOTAL_SIZE} bytes')
                    return {'error': f'Total file size exceeds {MAX_TOTAL_SIZE} bytes'}, 413

                encrypted_file_lib = self.encrypt_file(user, file)
                self.get_encrypted_file_size_mb(encrypted_file_lib)

                file_id = mongo_manager.insert_document(config_manager.get_mongo_config().get("user_files_collection"), {'file_lib': encrypted_file_lib, 'filename': file.filename, 'user': username, 'title': title}, use_GridFS=False)
                file_ids.append(file_id)
                Logger.info(f'File {file.filename} uploaded successfully')
            else:
                Logger.error('Invalid file type')
                return {'error': 'Invalid file type'}, 415

        Logger.info('Files uploaded successfully')
        return {'message': 'Files uploaded successfully'}, 201

    def get_encrypted_file_size_mb(self, encrypted_file_lib):
        total_size_bytes = (
                len(encrypted_file_lib["DER_lenght"]) +
                len(encrypted_file_lib["Ephemeral_public_key_der"]) +
                len(encrypted_file_lib["Nonce"]) +
                len(encrypted_file_lib["Tag"]) +
                len(encrypted_file_lib["Ciphertext"])
        )
        total_size_mb = total_size_bytes / (1024 * 1024)
        Logger.info(f'Encrypted file size: {total_size_mb} MB')

    def encrypt_file(self, user, file):
        public_key = ECC.import_key(user['PublicKey'])

        # Generate ephemeral key pair
        ephemeral_key = ECC.generate(curve='secp256r1')
        ephemeral_public_key = ephemeral_key.public_key()

        # ECDH: Compute shared secret
        shared_secret = ephemeral_key.d * public_key.pointQ
        shared_secret_bytes = shared_secret.x.to_bytes(32, 'big')

        # Derive AES key using HKDF
        aes_key = HKDF(shared_secret_bytes, 32, b'', SHA256, 1)

        # Encrypt file with AES-GCM
        nonce = get_random_bytes(16)
        cipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)

        ciphertext = b''
        while chunk := file.read(2 * 1024 * 1024):  # Read in 2MB chunks
            ciphertext += cipher.encrypt(chunk)
        tag = cipher.digest()

        # Prepare encrypted data (format: [DER length][DER][nonce][tag][ciphertext])
        ephemeral_public_key_der = ephemeral_public_key.export_key(format='DER')
        der_length = len(ephemeral_public_key_der).to_bytes(4, 'big')

        return {"DER_lenght": der_length, "Ephemeral_public_key_der": ephemeral_public_key_der, "Nonce": nonce, "Tag": tag,
                "Ciphertext": ciphertext}

# Resource for file download
class DownloadFile(Resource):
    def get(self):
        # Validate parameters
        parser = reqparse.RequestParser()
        parser.add_argument('filename', location='headers', type=str, required=True, help="Filename is required")
        parser.add_argument('user', location='headers', type=str, required=True, help="User is required")
        parser.add_argument('title', location='headers', type=str, required=True, help="Title is required")
        args = parser.parse_args()

        filename = args['filename']
        user = args['user']
        title = args['title']

        try:
            # Retrieve file from MongoDB
            files = mongo_manager.find_documents(config_manager.get_mongo_config().get("user_files_collection"), {'filename': filename, 'user': user, 'title': title}, use_GridFS=False)
            if not files:
                Logger.error('File not found')
                return {'error': 'File not found'}, 404

            file = files[0]
            Logger.info(f'File {filename} retrieved successfully')
            plain_file = self.decrypt_file(user, file["file_lib"])

            plain_file_path = 'decrypted_image.png'
            plain_file.save(plain_file_path)
            return send_file(plain_file_path, download_name=filename, as_attachment=True)
        except Exception as e:
            Logger.error(f'Error occurred: {str(e)}')
            return {'error': f'Error occurred: {str(e)}'}, 500

    def decrypt_file(self, user, file):
        with open('./keys/private_keys.json', 'r') as f:
            data = json.load(f)
            private_key = ECC.import_key([item for item in data if item['user'] == user][0]['private_key'])

        # Retrieve encrypted data
        ephemeral_public_key_der = file["Ephemeral_public_key_der"]
        nonce = file["Nonce"]
        tag = file["Tag"]
        ciphertext = file["Ciphertext"]

        # Import ephemeral public key
        ephemeral_public_key = ECC.import_key(ephemeral_public_key_der)

        # ECDH: Compute shared secret
        shared_secret = private_key.d * ephemeral_public_key.pointQ
        shared_secret_bytes = shared_secret.x.to_bytes(32, 'big')

        # Derive AES key
        aes_key = HKDF(shared_secret_bytes, 32, b'', SHA256, 1)

        # Decrypt
        cipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)

        # Logger.debug(plaintext)

        # Save decrypted content as PNG
        image = Image.open(io.BytesIO(plaintext))
        image.save('./decrypted_files/decrypted_image.png')

        return image

# Resource for file deletion
class DeleteFile(Resource):
    def delete(self):
        # Validate parameters
        parser = reqparse.RequestParser()
        parser.add_argument('filename', location='headers', type=str, required=True, help="Filename is required")
        parser.add_argument('user', location='headers', type=str, required=True, help="User is required")
        parser.add_argument('title', location='headers', type=str, required=True, help="Title is required")
        args = parser.parse_args()

        filename = args['filename']
        user = args['user']
        title = args['title']

        try:
            # Delete file from MongoDB
            result = mongo_manager.delete_documents(config_manager.get_mongo_config().get("user_files_collection"), {'filename': filename, 'user': user, 'title': title}, use_GridFS=True)
            if result.deleted_count == 0:
                Logger.error('File not found')
                return {'error': 'File not found'}, 404

            Logger.info(f'File {filename} deleted successfully')
            return {'message': 'File deleted successfully'}, 200
        except Exception as e:
            Logger.error(f'Error occurred: {str(e)}')
            return {'error': f'Error occurred: {str(e)}'}, 500