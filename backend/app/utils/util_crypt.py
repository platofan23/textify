import io
import json
import typing
from Cryptodome.Cipher import AES
from Cryptodome.Hash import SHA256
from Cryptodome.Protocol.KDF import HKDF
from Cryptodome.PublicKey import ECC
from Cryptodome.Random import get_random_bytes
from PIL import Image
from backend.app.utils import Logger


class Crypto_Manager:
    """
    Singleton class for performing file encryption and decryption using ECC and AES-GCM.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Crypto_Manager, cls).__new__(cls, *args, **kwargs)
        return cls._instance


    def __init__(self):
        if not hasattr(self, 'initialized'):
            try:
                with open('./keys/private_keys.json', 'r') as f:
                    self._private_ECC_keys_json = json.load(f)
            except Exception as e:
                Logger.error(f"Failed to load private keys: {e}")
                self._private_ECC_keys_json = None
            self.initialized = True
            Logger.info("Crypt class initialized successfully.")

    def encrypt_file(self, user: dict, file: typing.IO) -> dict:
        """
        Encrypts the given file using an ephemeral ECC key pair and AES-GCM.

        Args:
            user (dict): User document containing the user's public key.
            file (typing.IO): The file object to encrypt.

        Returns:
            dict: A dictionary containing the encrypted file components.
        """
        public_key = ECC.import_key(user['PublicKey'])

        # Generate ephemeral ECC key pair
        ephemeral_key = ECC.generate(curve='secp256r1')
        ephemeral_public_key = ephemeral_key.public_key()

        # Compute shared secret using ECDH
        shared_secret = ephemeral_key.d * public_key.pointQ
        shared_secret_bytes = shared_secret.x.to_bytes(32, 'big')

        # Derive an AES key via HKDF
        aes_key = HKDF(shared_secret_bytes, 32, b'', SHA256, 1)

        # Encrypt file with AES-GCM
        nonce = get_random_bytes(16)
        cipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)

        ciphertext = b""
        # Read in 2MB chunks
        while chunk := file.read(2 * 1024 * 1024):
            ciphertext += cipher.encrypt(chunk)
        tag = cipher.digest()

        # Export ephemeral public key in DER format and record its length
        ephemeral_public_key_der = ephemeral_public_key.export_key(format='DER')
        der_length = len(ephemeral_public_key_der).to_bytes(4, 'big')

        return {
            "DER_length": der_length,  # Correct key name used.
            "Ephemeral_public_key_der": ephemeral_public_key_der,
            "Nonce": nonce,
            "Tag": tag,
            "Ciphertext": ciphertext
        }

    def decrypt_file(self, user: str, file: dict) -> bytes:
        """
        Decrypts an encrypted file using the private key corresponding to the user.

        Args:
            user (str): The username used to lookup the private key.
            file (dict): The dictionary containing encrypted file components.

        Returns:
            bytes: The decrypted file content.
        """
        try:
            with open('./keys/private_keys.json', 'r') as f:
                data = json.load(f)
                private_key_str = [item for item in data if item['user'] == user][0]['private_key']
                private_key = ECC.import_key(private_key_str)
        except Exception as e:
            Logger.error(f"Error loading private key for user {user}: {e}")
            raise

        # Retrieve encrypted components
        ephemeral_public_key_der = file["Ephemeral_public_key_der"]
        nonce = file["Nonce"]
        tag = file["Tag"]
        ciphertext = file["Ciphertext"]

        # Import ephemeral public key
        ephemeral_public_key = ECC.import_key(ephemeral_public_key_der)

        # Compute shared secret using ECDH
        shared_secret = private_key.d * ephemeral_public_key.pointQ
        shared_secret_bytes = shared_secret.x.to_bytes(32, 'big')

        # Derive AES key
        aes_key = HKDF(shared_secret_bytes, 32, b'', SHA256, 1)

        # Decrypt using AES-GCM
        cipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)

        Logger.info(f"File decryption completed successfully.")
        return plaintext

    def decrypt_png(self, user: str, file: dict, file_name: str):
        """
        Decrypts an encrypted PNG file and saves it to disk.

        Args:
            user (str): The username used to lookup the private key.
            file (dict): The dictionary containing encrypted file components.
            file_name (str): The file name for saving the decrypted image.

        Returns:
            PIL.Image.Image: The decrypted image.
        """
        plaintext = self.decrypt_file(user, file, file_name)
        image = Image.open(io.BytesIO(plaintext))
        image.save(f'./decrypted_files/decrypted_{file_name}.png')
        return image


    def get_encrypted_file_size_mb(self, encrypted_file_lib: dict) -> float:
        """
        Calculates and returns the size of the encrypted file in megabytes.

        Args:
            encrypted_file_lib (dict): Dictionary containing encrypted file components.

        Returns:
            float: Size of the encrypted file in MB.
        """
        total_size_bytes = (
                len(encrypted_file_lib["DER_length"]) +
                len(encrypted_file_lib["Ephemeral_public_key_der"]) +
                len(encrypted_file_lib["Nonce"]) +
                len(encrypted_file_lib["Tag"]) +
                len(encrypted_file_lib["Ciphertext"])
        )
        return total_size_bytes / (1024 * 1024)

    def encrypt_orc_text(self, user, text: list[dict[str, int]]):
        return self.encrypt_file(user, io.BytesIO(json.dumps(text).encode()))

    def decrypt_ocr_text(self, username, file: dict):
        return json.loads(self._decrypt_file(username, file))
