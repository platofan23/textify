import io
import json
import typing
import os
import threading
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import HKDF
from Crypto.PublicKey import ECC
from Crypto.Random import get_random_bytes
from PIL import Image
from backend.app.utils import Logger


class Crypt:
    _instance = None
    _private_ECC_keys_json = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Crypt, cls).__new__(cls, *args, **kwargs)
        return cls._instance


    def __init__(self):
        if not hasattr(self, 'initialized'):
            Logger.info("Initializing Crypt class.")
            with open('./keys/private_keys.json', 'r') as f:
                _private_ECC_keys_json = json.load(f)
            self.initialized = True
            Logger.info("Crypt class initialized successfully.")


    def encrypt_file(self, user, file: typing.IO):
        Logger.info("Starting file encryption.")
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

        Logger.info("File encryption completed successfully.")
        return {"DER_lenght": der_length, "Ephemeral_public_key_der": ephemeral_public_key_der, "Nonce": nonce, "Tag": tag,
                "Ciphertext": ciphertext}


    def _decrypt_file(self, user, file: dict, file_name: str):
        Logger.info(f"Starting file decryption for {file_name}.")
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

        Logger.info(f"File decryption for {file_name} completed successfully.")
        return plaintext


    def decrypt_png(self, user, file: dict, file_name: str):
        Logger.info(f"Starting PNG decryption for {file_name}.")
        plaintext = self._decrypt_file(user, file, file_name)

        # Save decrypted content as PNG
        file_path = f'./decrypted_files/decrypted_{file_name}'
        image = Image.open(io.BytesIO(plaintext))
        image.save(file_path)

        # Schedule file deletion after 1 minute
        timer = threading.Timer(60, self.delete_file, args=[file_path])
        timer.start()

        Logger.info(f"PNG decryption for {file_name} completed successfully. File saved at {file_path}.")
        return file_path


    def delete_file(self, file_path):
        try:
            os.remove(file_path)
            Logger.info(f'File {file_path} deleted successfully')
        except Exception as e:
            Logger.error(f'Error deleting file {file_path}: {str(e)}')


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