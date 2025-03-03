import io
import json
import secrets
import typing
from datetime import datetime, timedelta
from Cryptodome.Cipher import AES
from Cryptodome.Hash import SHA256
from Cryptodome.Protocol.KDF import HKDF
from Cryptodome.PublicKey import ECC
from Cryptodome.Random import get_random_bytes
from PIL import Image
from backend.app.utils import Logger


class Crypto_Manager:
    """
    Singleton class for performing cryptographic operations including ECC key generation,
    file encryption/decryption, and authorization key management.
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
            Logger.info("Crypto_Manager initialized successfully.")

    def generate_ecc_keys(self, username: str) -> str:
        """
        Generates an ECC key pair and stores the private key securely.

        Args:
            username (str): The username for whom the keys are generated.

        Returns:
            str: The generated public key in PEM format.
        """
        private_key = ECC.generate(curve='secp256r1')
        Logger.info(f'Generated ECC keys for {username}')

        private_keys_path = './keys/private_keys.json'
        try:
            with open(private_keys_path, 'r+') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []
                if not isinstance(data, list):
                    data = []
                data.append({'user': username, 'private_key': private_key.export_key(format='PEM')})
                f.seek(0)
                json.dump(data, f)
                f.truncate()
        except FileNotFoundError:
            with open(private_keys_path, 'w') as f:
                json.dump([{'user': username, 'private_key': private_key.export_key(format='PEM')}], f)

        return private_key.public_key().export_key(format='PEM')

    def encrypt_file(self, user: dict, file: typing.IO) -> dict:
        """
        Encrypts a given file or buffer using ECC and AES-GCM.

        Args:
            user (dict): User document containing the user's public key.
            file (typing.IO): The file object or buffer to encrypt.

        Returns:
            dict: A dictionary containing the encrypted file components.
        """
        public_key = ECC.import_key(user['PublicKey'])
        ephemeral_key = ECC.generate(curve='secp256r1')
        ephemeral_public_key = ephemeral_key.public_key()
        shared_secret = ephemeral_key.d * public_key.pointQ
        shared_secret_bytes = shared_secret.x.to_bytes(32, 'big')
        aes_key = HKDF(shared_secret_bytes, 32, b'', SHA256, 1)
        nonce = get_random_bytes(16)
        cipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)

        # Read and encrypt file content
        file.seek(0)
        ciphertext = cipher.encrypt(file.read())
        tag = cipher.digest()
        ephemeral_public_key_der = ephemeral_public_key.export_key(format='DER')

        return {
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

        ephemeral_public_key_der = file["Ephemeral_public_key_der"]
        nonce = file["Nonce"]
        tag = file["Tag"]
        ciphertext = file["Ciphertext"]
        ephemeral_public_key = ECC.import_key(ephemeral_public_key_der)
        shared_secret = private_key.d * ephemeral_public_key.pointQ
        shared_secret_bytes = shared_secret.x.to_bytes(32, 'big')
        aes_key = HKDF(shared_secret_bytes, 32, b'', SHA256, 1)
        cipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        Logger.info("File decryption completed successfully.")
        return plaintext

    def encrypt_audio(self, user: typing.Union[dict, str], file: typing.IO) -> dict:
        """
        Encrypts a given file or buffer using ECC and AES-GCM.

        Args:
            user (dict or str): A user dictionary containing 'PublicKey' or a username string.
            file (typing.IO): The file object or buffer to encrypt.

        Returns:
            dict: A dictionary containing the encrypted file components.
        """
        # Falls der Benutzer als String übergeben wird, PublicKey aus der Datenbank oder Datei laden
        if isinstance(user, str):
            try:
                with open('./keys/private_keys.json', 'r') as f:
                    data = json.load(f)
                    entry = next((item for item in data if item['user'] == user), None)
                    if entry is None:
                        raise ValueError(f"No key found for user '{user}'.")
                    private_key = ECC.import_key(entry['private_key'])
                    public_key = private_key.public_key()
                    user = {"PublicKey": public_key.export_key(format='PEM')}
            except Exception as e:
                Logger.error(f"Failed to retrieve key for user {user}: {e}")
                raise ValueError(f"Failed to retrieve key for user {user}: {e}")

        elif "PublicKey" not in user:
            raise ValueError("User must be a dictionary containing a 'PublicKey' field.")

        public_key = ECC.import_key(user['PublicKey'])
        ephemeral_key = ECC.generate(curve='secp256r1')
        ephemeral_public_key = ephemeral_key.public_key()
        shared_secret = ephemeral_key.d * public_key.pointQ
        shared_secret_bytes = shared_secret.x.to_bytes(32, 'big')
        aes_key = HKDF(shared_secret_bytes, 32, b'', SHA256, 1)
        nonce = get_random_bytes(16)
        cipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)

        # Read and encrypt file content
        file.seek(0)
        ciphertext = cipher.encrypt(file.read())
        tag = cipher.digest()
        ephemeral_public_key_der = ephemeral_public_key.export_key(format='DER')

        return {
            "Ephemeral_public_key_der": ephemeral_public_key_der,
            "Nonce": nonce,
            "Tag": tag,
            "Ciphertext": ciphertext
        }

    def decrypt_audio(self, user: str, file: dict) -> io.BytesIO:
        """
        Decrypts an encrypted file or audio buffer using the private key corresponding to the user.

        Args:
            user (str): The username used to lookup the private key.
            file (dict): The dictionary containing encrypted file components.

        Returns:
            io.BytesIO: A BytesIO stream containing the decrypted file content.
        """
        try:
            # Load the private key for the user
            with open('./keys/private_keys.json', 'r') as f:
                data = json.load(f)
                private_key_str = [item for item in data if item['user'] == user][0]['private_key']
                private_key = ECC.import_key(private_key_str)
        except Exception as e:
            Logger.error(f"Error loading private key for user {user}: {e}")
            raise

        try:
            # Retrieve encryption components
            ephemeral_public_key_der = file["Ephemeral_public_key_der"]
            nonce = file["Nonce"]
            tag = file["Tag"]
            ciphertext = file["Ciphertext"]

            # Import the ephemeral public key
            ephemeral_public_key = ECC.import_key(ephemeral_public_key_der)

            # Compute the shared secret
            shared_secret = private_key.d * ephemeral_public_key.pointQ
            shared_secret_bytes = shared_secret.x.to_bytes(32, 'big')

            # Derive the AES key
            aes_key = HKDF(shared_secret_bytes, 32, b'', SHA256, 1)

            # Decrypt using AES-GCM
            cipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
            plaintext = cipher.decrypt_and_verify(ciphertext, tag)

            Logger.info("File decryption completed successfully.")

            # Convert decrypted data into a BytesIO stream (for audio or file handling)
            decrypted_stream = io.BytesIO(plaintext)
            decrypted_stream.seek(0)  # Reset the stream position

            return decrypted_stream

        except Exception as e:
            Logger.error(f"Decryption error: {e}")
            raise ValueError("Failed to decrypt the file") from e

    def encrypt_string(self, user, plaintext: str) -> dict:
        """
        Encrypts a plaintext string using ECC and AES-GCM.

        Args:
            user (dict or str): A user dictionary containing 'PublicKey' or a username string.
            plaintext (str): The string to encrypt.

        Returns:
            dict: A dictionary containing the encrypted string components.
        """
        if not isinstance(plaintext, str):
            plaintext = str(plaintext)

        # Falls nur der Benutzername übergeben wurde oder kein PublicKey vorhanden ist, PublicKey laden
        if isinstance(user, str) or "PublicKey" not in user:
            user = self._get_user_with_public_key(user)  # Automatische PublicKey-Ladung

        if "PublicKey" not in user:
            raise ValueError(f"PublicKey for user '{user.get('Username', 'Unknown')}' could not be found.")

        return self.encrypt_file(user, io.BytesIO(plaintext.encode('utf-8')))

    def decrypt_string(self, user: str, encrypted_data: dict) -> str:
        """
        Decrypts an encrypted string using the private key corresponding to the user.

        Args:
            user (str): The username used to lookup the private key.
            encrypted_data (dict): The dictionary containing encrypted string components.

        Returns:
            str: The decrypted plaintext string.
        """
        plaintext_bytes = self.decrypt_file(user, encrypted_data)
        return plaintext_bytes.decode('utf-8')

    def add_key(self, username: str, collection) -> str:
        """
        Generates an authorization key valid for 7 days and stores it in the user's record.

        Args:
            username (str): The username for whom the key is created.
            collection: The MongoDB collection object.

        Returns:
            str: The generated authorization key.
        """
        expiration_date = datetime.now() + timedelta(days=7)
        key = secrets.token_hex(32)
        collection.update_one(
            {'Username': username},
            {'$push': {'AuthorizationKeys': {'Key': key, 'ExpiresAt': expiration_date}}}
        )
        return key

    def delete_expired_keys(self, collection):
        """
        Removes expired authorization keys from the database.

        Args:
            collection: The MongoDB collection object.
        """
        current_time = datetime.now()
        Logger.info('Deleting expired authorization keys')
        collection.update_many(
            {},
            {'$pull': {'AuthorizationKeys': {'ExpiresAt': {'$lt': current_time}}}}
        )

    def _get_user_with_public_key(self, username: str) -> dict:
        """
        Retrieves the public key for a given username.

        Args:
            username (str): The username whose public key is needed.

        Returns:
            dict: A dictionary containing 'PublicKey'.
        """
        try:
            with open('./keys/private_keys.json', 'r') as f:
                data = json.load(f)
                user_data = next((item for item in data if item['user'] == username), None)

                if user_data is None:
                    raise ValueError(f"No key found for user '{username}'.")

                private_key = ECC.import_key(user_data['private_key'])
                public_key = private_key.public_key().export_key(format='PEM')

                return {"Username": username, "PublicKey": public_key}

        except FileNotFoundError:
            raise ValueError(f"Key file not found for user '{username}'.")
        except Exception as e:
            raise ValueError(f"Failed to retrieve PublicKey for user '{username}': {e}")

    @staticmethod
    def get_encrypted_file_size_mb( encrypted_file_lib: dict) -> float:
        """
        Calculates and returns the size of the encrypted file in megabytes.

        Args:
            encrypted_file_lib (dict): Dictionary containing encrypted file components.

        Returns:
            float: Size of the encrypted file in MB.
        """
        total_size_bytes = (
                len(encrypted_file_lib["Ephemeral_public_key_der"]) +
                len(encrypted_file_lib["Nonce"]) +
                len(encrypted_file_lib["Tag"]) +
                len(encrypted_file_lib["Ciphertext"])
        )
        return total_size_bytes / (1024 * 1024)
