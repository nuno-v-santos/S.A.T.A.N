import unittest
from .encryption import RSAEncryption, AES256Encryption
from .keys import RSAKeyManager, AES256KeyManager

TEST_STRING1 = b'SIRS is fun!'
TEST_STRING2 = b'We <3 Security'

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
        encrypted = self.cipher.encrypt(original, iv=self.iv)
        self.assertNotEqual(original, encrypted)
        decrypted = self.cipher.decrypt(encrypted, iv=self.iv)
        self.assertEqual(original, decrypted)

    def test_same_plaintext_different_iv(self):
        first_encrypted = self.cipher.encrypt(TEST_STRING1)
        second_encrypted = self.cipher.encrypt(TEST_STRING1)
        self.assertNotEqual(first_encrypted, second_encrypted)


if __name__ == '__main__':
    unittest.main()
