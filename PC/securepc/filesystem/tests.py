import os
import tempfile
import unittest

from securepc.filesystem.encryption import encrypt_file, decrypt_file
from securepc.security import keys


class EncryptionTestCase(unittest.TestCase):
    TEST_STRING = b'RivestShamirAdleman'
    TEST_IV = b'Super Secret IV!'

    def setUp(self):
        key_manager = keys.AES256KeyManager()
        self.key = key_manager.create_key(b'AdvancedEncryptionStandard')

    def test_encrypt_and_decrypt_file(self):
        fd, path = tempfile.mkstemp()
        os.write(fd, self.TEST_STRING)
        os.close(fd)

        encrypt_file(path, self.key)

        with open(path, 'rb') as f:
            self.assertNotEqual(self.TEST_STRING, f.read())

        decrypt_file(path, self.key)

        with open(path, 'rb') as f:
            self.assertEqual(self.TEST_STRING, f.read())

        os.remove(path)


if __name__ == '__main__':
    unittest.main()
