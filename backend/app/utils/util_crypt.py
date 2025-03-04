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
from backend.app.utils import Logger


class Crypto_Manager:
    """
    Singleton class for performing cryptographic operations, including ECC key generation,
    file encryption/decryption, and authorization key management.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Crypto_Manager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self._load_private_keys()
            self.initialized = True
            Logger.info("Crypto_Manager initialized successfully.")

    def _load_private_keys(self):
        """
        Loads private ECC keys from the local file. If the file is not found or corrupted, initializes with None.
        """
        try:
            with open("./keys/private_keys.json", "r") as f:
                self._private_ECC_keys_json = json.load(f)
        except Exception as e:
            Logger.error(f"Failed to load private keys: {e}")
            self._private_ECC_keys_json = None

    def generate_ecc_keys(self, username: str) -> str:
        """
        Generates an ECC key pair and stores the private key securely.

        Args:
            username (str): The username for whom the keys are generated.

        Returns:
            str: The generated public key in PEM format.
        """
        private_key = ECC.generate(curve="secp256r1")
        Logger.info(f"Generated ECC keys for {username}")

        private_keys_path = "./keys/private_keys.json"
        self._store_private_key(private_keys_path, username, private_key)
        return private_key.public_key().export_key(format="PEM")

    def _store_private_key(self, file_path: str, username: str, private_key):
        """
        Stores a private ECC key in a JSON file.

        Args:
            file_path (str): Path to the private keys file.
            username (str): Username associated with the key.
            private_key: ECC private key object.
        """
        try:
            with open(file_path, "r+") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []
                if not isinstance(data, list):
                    data = []
                data.append({"user": username, "private_key": private_key.export_key(format="PEM")})
                f.seek(0)
                json.dump(data, f)
                f.truncate()
        except FileNotFoundError:
            with open(file_path, "w") as f:
                json.dump([{"user": username, "private_key": private_key.export_key(format="PEM")}], f)

    def _load_user_key(self, user: str):
        """
        Retrieves the ECC private key for the given user from storage.

        Args:
            user (str): Username.

        Returns:
            ECC key object.
        """
        try:
            with open("./keys/private_keys.json", "r") as f:
                data = json.load(f)
                private_key_str = next(item["private_key"] for item in data if item["user"] == user)
                return ECC.import_key(private_key_str)
        except Exception as e:
            Logger.error(f"Error loading private key for user {user}: {e}")
            raise

    def _derive_aes_key(self, shared_secret) -> bytes:
        """
        Derives a 32-byte AES key from the shared ECC secret using HKDF.

        Args:
            shared_secret: Shared secret computed from ECC keys.

        Returns:
            bytes: 32-byte AES key.
        """
        shared_secret_bytes = shared_secret.x.to_bytes(32, "big")
        return HKDF(shared_secret_bytes, 32, b"", SHA256, 1)

    def encrypt_file(self, user: dict, file: typing.IO) -> dict:
        """
        Encrypts a file using ECC and AES-GCM.

        Args:
            user (dict): User object containing 'PublicKey'.
            file (typing.IO): File object to encrypt.

        Returns:
            dict: Encrypted file components.
        """
        public_key = ECC.import_key(user["PublicKey"])
        ephemeral_key = ECC.generate(curve="secp256r1")
        shared_secret = ephemeral_key.d * public_key.pointQ
        aes_key = self._derive_aes_key(shared_secret)

        nonce = get_random_bytes(16)
        cipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)

        file.seek(0)
        ciphertext = cipher.encrypt(file.read())
        tag = cipher.digest()

        return {
            "Ephemeral_public_key_der": ephemeral_key.public_key().export_key(format="DER"),
            "Nonce": nonce,
            "Tag": tag,
            "Ciphertext": ciphertext,
        }

    def decrypt_file(self, user: str, file: dict) -> bytes:
        """
        Decrypts an encrypted file.

        Args:
            user (str): Username.
            file (dict): Encrypted file components.

        Returns:
            bytes: Decrypted file content.
        """
        private_key = self._load_user_key(user)
        ephemeral_public_key = ECC.import_key(file["Ephemeral_public_key_der"])
        shared_secret = private_key.d * ephemeral_public_key.pointQ
        aes_key = self._derive_aes_key(shared_secret)

        cipher = AES.new(aes_key, AES.MODE_GCM, nonce=file["Nonce"])
        plaintext = cipher.decrypt_and_verify(file["Ciphertext"], file["Tag"])

        Logger.info("File decryption completed successfully.")
        return plaintext

    def encrypt_audio(self, user: typing.Union[dict, str], file: typing.IO) -> dict:
        """
        Encrypts an audio file using ECC and AES-GCM.

        Args:
            user (dict or str): User dictionary containing 'PublicKey' or username.
            file (typing.IO): File object to encrypt.

        Returns:
            dict: Encrypted file components.
        """
        if isinstance(user, str):
            user = {"PublicKey": self._load_user_key(user).public_key().export_key(format="PEM")}

        if isinstance(file, bytes):
            file = io.BytesIO(file)
        elif isinstance(file, str):
            with open(file, "rb") as f:
                file = io.BytesIO(f.read())

        if not isinstance(file, io.BytesIO):
            raise TypeError("Invalid file type. Must be bytes or file path.")

        file.seek(0)
        return self.encrypt_file(user, file)

    def decrypt_audio(self, user: str, file: dict) -> io.BytesIO:
        """
        Decrypts an encrypted audio file.

        Args:
            user (str): Username.
            file (dict): Encrypted file components.

        Returns:
            io.BytesIO: Decrypted file content as a BytesIO stream.
        """
        plaintext = self.decrypt_file(user, file)
        decrypted_stream = io.BytesIO(plaintext)
        decrypted_stream.seek(0)
        return decrypted_stream

    def encrypt_string(self, user, plaintext: str) -> dict:
        """
        Encrypts a plaintext string.

        Args:
            user (dict or str): User object or username.
            plaintext (str): Text to encrypt.

        Returns:
            dict: Encrypted string components.
        """
        return self.encrypt_file(user, io.BytesIO(plaintext.encode("utf-8")))

    def decrypt_string(self, user: str, encrypted_data: dict) -> str:
        """
        Decrypts an encrypted string.

        Args:
            user (str): Username.
            encrypted_data (dict): Encrypted string components.

        Returns:
            str: Decrypted plaintext.
        """
        return self.decrypt_file(user, encrypted_data).decode("utf-8")

    def add_key(self, username: str, collection) -> str:
        """
        Generates and stores an authorization key valid for 7 days.

        Args:
            username (str): Username.
            collection: MongoDB collection.

        Returns:
            str: Generated authorization key.
        """
        key = secrets.token_hex(32)
        collection.update_one(
            {"Username": username},
            {"$push": {"AuthorizationKeys": {"Key": key, "ExpiresAt": datetime.now() + timedelta(days=7)}}},
        )
        return key
