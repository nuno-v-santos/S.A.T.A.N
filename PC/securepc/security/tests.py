import unittest
import tempfile
import os
import io

from securepc.security.encryption import RSAEncryption, AES256Encryption
from securepc.security.keys import RSAKeyManager, AES256KeyManager

TEST_STRING1 = b'SIRS is fun!'
TEST_STRING2 = b'We <3 Security'

TEST_PASSWORD = 'All play and no work makes Jack a happy boy'

class RSATestCase(unittest.TestCase):

    def setUp(self):
        self.key_manager = RSAKeyManager()
        self.key_pair = self.key_manager.create_key_pair(2048)
        self.public_key_cipher = RSAEncryption(self.key_pair.public_key)
        self.private_key_cipher = RSAEncryption(self.key_pair.private_key)

    def test_generated_key_size(self):
        FIRST_KEY_SIZE = 1024
        SECOND_KEY_SIZE = 2048
        key1 = self.key_manager.create_key_pair(FIRST_KEY_SIZE)
        key2 = self.key_manager.create_key_pair(SECOND_KEY_SIZE)

        self.assertEqual(key1.public_key.size_in_bits(), key1.private_key.size_in_bits())
        self.assertEqual(key2.public_key.size_in_bits(), key2.private_key.size_in_bits())
        self.assertEqual(key1.public_key.size_in_bits(), FIRST_KEY_SIZE)
        self.assertEqual(key2.public_key.size_in_bits(), SECOND_KEY_SIZE)

    def test_encryption_and_decryption(self):
        original = TEST_STRING1
        encrypted = self.public_key_cipher.encrypt(original)
        self.assertNotEqual(original, encrypted)
        decrypted = self.private_key_cipher.decrypt(encrypted)
        self.assertEqual(original, decrypted)

    def test_save_and_load_key_file_no_password(self):
        fd, path = tempfile.mkstemp()
        os.close(fd)

        self.key_manager.store_key(self.key_pair.private_key, path)
        loaded_key = self.key_manager.load_key(path)

        os.remove(path)

        self.assertEqual(self.key_pair.private_key, loaded_key)

    def test_save_and_load_key_file_password(self):
        fd, path = tempfile.mkstemp()
        os.close(fd)

        self.key_manager.store_key(self.key_pair.private_key, path, TEST_PASSWORD)
        loaded_key = self.key_manager.load_key(path, TEST_PASSWORD)

        os.remove(path)

        self.assertEqual(self.key_pair.private_key, loaded_key)

    def test_save_and_load_key_stream_no_password(self):
        key = self.key_pair.public_key

        with io.BytesIO() as file:
            self.key_manager.store_key(key, file)
            file.seek(0)
            loaded_key = self.key_manager.load_key(file)

        self.assertEqual(key, loaded_key)

    def test_save_and_load_key_stream_password(self):
        key = self.key_pair.public_key

        with io.BytesIO() as file:
            self.key_manager.store_key(key, file, TEST_PASSWORD)
            file.seek(0)
            loaded_key = self.key_manager.load_key(file, TEST_PASSWORD)

        self.assertEqual(key, loaded_key)


class AES256TestCase(unittest.TestCase):

    def setUp(self):
        self.key_manager = AES256KeyManager()
        self.static_seed = b'5up3r Dup3r S3cr3t P455w0rd'
        self.iv = b'S3cur3 R4nd0m 1V'
        self.key = self.key_manager.create_key(self.static_seed)
        self.cipher = AES256Encryption(self.key, AES256Encryption.MODE_CBC)

    def test_deterministic_key(self):
        new_key = self.key_manager.create_key(self.static_seed)
        self.assertEqual(self.key, new_key)

    def test_encryption_and_decryption(self):
        original = TEST_STRING1
        encrypted = self.cipher.encrypt(original)
        self.assertNotEqual(original, encrypted)
        decrypted = self.cipher.decrypt(encrypted)
        self.assertEqual(original, decrypted)

    def test_same_plaintext_different_iv(self):
        first_encrypted = self.cipher.encrypt(TEST_STRING1)
        second_encrypted = self.cipher.encrypt(TEST_STRING1)
        self.assertNotEqual(first_encrypted, second_encrypted)

    def test_eax_not_tampered(self):
        original = TEST_STRING1
        encrypted = self.cipher.encrypt(original, mode=self.cipher.MODE_EAX)
        self.assertNotEqual(original, encrypted)
        decrypted = self.cipher.decrypt(encrypted)
        self.assertEqual(original, decrypted)

    def test_eax_tampered(self):
        original = TEST_STRING1
        encrypted = self.cipher.encrypt(original, mode=self.cipher.MODE_EAX)
        encrypted = encrypted[:4] + bytes([(encrypted[5] + 1) % 255]) + encrypted[6:]
        try:
            self.cipher.decrypt(encrypted)
        except:
            return
        self.fail("Decrypt method did not throw an exception")

    def test_save_and_load_key_file_no_password(self):
        fd, path = tempfile.mkstemp()
        os.close(fd)

        self.key_manager.store_key(self.key, path)
        loaded_key = self.key_manager.load_key(path)

        os.remove(path)

        self.assertEqual(self.key, loaded_key)

    def test_save_and_load_key_file_password(self):
        fd, path = tempfile.mkstemp()
        os.close(fd)

        self.key_manager.store_key(self.key, path, TEST_PASSWORD)
        loaded_key = self.key_manager.load_key(path, TEST_PASSWORD)

        os.remove(path)

        self.assertEqual(self.key, loaded_key)

    def test_save_and_load_key_stream_no_password(self):
        with io.BytesIO() as file:
            self.key_manager.store_key(self.key, file)
            file.seek(0)
            loaded_key = self.key_manager.load_key(file)

        self.assertEqual(self.key, loaded_key)

    def test_save_and_load_key_stream_password(self):
        with io.BytesIO() as file:
            self.key_manager.store_key(self.key, file, TEST_PASSWORD)
            file.seek(0)
            loaded_key = self.key_manager.load_key(file, TEST_PASSWORD)

        self.assertEqual(self.key, loaded_key)


if __name__ == '__main__':
    unittest.main()
