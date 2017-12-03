import logging
import qrcode

from messaging.communication import BluetoothCommunication
from security.keys import RSAKeyManager
from security.encryption import RSAEncryption, AES256Encryption


def main():
    # app = wx.App()
    # c = Controller()
    # app.MainLoop()
    logging.getLogger().setLevel(logging.DEBUG)
    logging.debug("Generating RSA Key Pair")
    key_pair = RSAKeyManager().create_key_pair(2048)
    rsa_private_cipher = RSAEncryption(key_pair.private_key)
    logging.debug("Starting bluetooth interface")
    with BluetoothCommunication() as bluetooth_interface:
        bluetooth_interface.accept()
        logging.debug("Creating QR Code with public key")
        qr = qrcode.make(key_pair.public_key.exportKey())
        qr.show()

        logging.debug("Receiving session key")
        session_key = bluetooth_interface.receive(256)
        logging.debug("Decrypting session key")
        session_key = rsa_private_cipher.decrypt(session_key)
        aes_cipher = AES256Encryption(session_key, mode=AES256Encryption.MODE_CBC)

        logging.debug("Receiving phone's public key")
        phone_key = bluetooth_interface.receive(480)
        iv, phone_key = phone_key[:16], phone_key[16:]
        logging.debug("Decrypting phone's public key")
        phone_key = aes_cipher.decrypt(phone_key, iv=iv)
        logging.debug("Phone key is {}".format(phone_key))

        logging.debug("Receiving Disk Encryption Key")
        disk_key = bluetooth_interface.receive(64)
        logging.debug("Decrypting Disk Encryption Key")
        iv, disk_key = disk_key[:16], disk_key[16:]
        disk_key = aes_cipher.decrypt(disk_key, iv=iv)
        logging.debug("Disk Encryption Key (encrypted by Master Encryption Key) is {}".format(disk_key.hex()))
if __name__ == '__main__':
    main()
