import io
import json
import typing
from pydoc import plaintext

from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import HKDF
from Crypto.PublicKey import ECC
from Crypto.Random import get_random_bytes
from PIL import Image


class Crypt:
    _instance = None
    _private_ECC_keys_json = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Crypt, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            # Initialize your class here
            with open('./keys/private_keys.json', 'r') as f:
                _private_ECC_keys_json = json.load(f)
            self.initialized = True


    def encrypt_file(self, user, file: typing.IO):
        # Encrypt file
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

    def _decrypt_file(self, user, file: dict, file_name: str):
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

        return plaintext


    def decrypt_png(self, user, file: dict, file_name: str):
        plaintext = self._decrypt_file(user, file, file_name)

        # Save decrypted content as PNG
        image = Image.open(io.BytesIO(plaintext))
        image.save(f'./decrypted_files/decrypted_{file_name}.png')

        return image