"""
This class provides AES encryption and decryption functionalities.

Attributes:
    None

Methods:
    __init__: Constructor method to initialize an AESCipher object.
    encrypt: Method to encrypt plaintext using AES encryption.
    decrypt: Method to decrypt ciphertext using AES decryption.
    _pad: Internal method to pad plaintext for AES encryption.
    _unpad: Static method to unpad decrypted plaintext.
"""

import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class AESCipher(object):
    def __init__(self, key):
        """
        Constructor method to initialize an AESCipher object.

        Args:
            key (str): The encryption key.

        Attributes:
            bs (int): The block size for AES encryption.
            key (bytes): The hashed encryption key.
        """
        self.bs = AES.block_size
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        """
        Encrypt plaintext using AES encryption.

        Args:
            raw (bytes): The plaintext to be encrypted.

        Returns:
            bytes: The encrypted ciphertext.
        """
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        """
        Decrypt ciphertext using AES decryption.

        Args:
            enc (bytes): The ciphertext to be decrypted.

        Returns:
            bytes: The decrypted plaintext.
        """
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:]))

    def _pad(self, s):
        """
        Pad plaintext for AES encryption.

        Args:
            s (bytes): The plaintext to be padded.

        Returns:
            bytes: The padded plaintext.
        """
        return pad(s, AES.block_size)

    @staticmethod
    def _unpad(s):
        """
        Unpad decrypted plaintext.

        Args:
            s (bytes): The plaintext to be unpadded.

        Returns:
            bytes: The unpadded plaintext.
        """
        return unpad(s, AES.block_size)

if __name__ == "__main__":
    aes_m = AESCipher('ariel')
    raw = b'hello'
    res = aes_m.encrypt(raw)
    res = aes_m.decrypt(res)
    print(res)
