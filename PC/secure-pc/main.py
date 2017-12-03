import logging
import qrcode
import time

from messaging.communication import BluetoothCommunication
from security.keys import RSAKeyManager, AES256KeyManager, RSA
from security.encryption import RSAEncryption, AES256Encryption


def main():
    # app = wx.App()
    # c = Controller()
    # app.MainLoop()
    logging.getLogger().setLevel(logging.DEBUG)
    logging.debug("Generating RSA Key Pair")
    key_pair = RSAKeyManager().create_key_pair(2048)
    rsa_private_cipher = RSAEncryption(key_pair.private_key)
    with BluetoothCommunication() as bluetooth_interface:
        logging.debug("Begin pairing.")
        bluetooth_interface.accept()
        logging.debug("Creating QR Code with public key")
        qr = qrcode.make(key_pair.public_key.exportKey())
        qr.show()

        logging.debug("Receiving session key")
        session_key = bluetooth_interface.receive(256) # Receive TEK
        logging.debug("Decrypting session key")
        session_key = rsa_private_cipher.decrypt(session_key)
        aes_cipher = AES256Encryption(session_key, mode=AES256Encryption.MODE_CBC)

        logging.debug("Receiving phone's public key")
        phone_key = bluetooth_interface.receive(480) # Receive IV | phone_public[TEK]
        iv, phone_key = phone_key[:16], phone_key[16:]
        logging.debug("Decrypting phone's public key")
        phone_key = aes_cipher.decrypt(phone_key, iv=iv)
        logging.debug("Phone key is {}".format(phone_key))

        logging.debug("Receiving Disk Encryption Key (encrypted by Master Encryption Key)")
        disk_key_mek = bluetooth_interface.receive(80) # receive IV | DEK(MEK)[TEK]
        logging.debug("Decrypting Disk Encryption Key (MEK)")
        iv, disk_key_mek = disk_key_mek[:16], disk_key_mek[16:]
        disk_key_mek = aes_cipher.decrypt(disk_key_mek, iv=iv)
        logging.debug("Disk Encryption Key (MEK) is {}".format(disk_key_mek.hex()))

        logging.debug("Receiving Disk Encryption Key (unencrypted)")
        disk_key = bluetooth_interface.receive(64)
        iv, disk_key = disk_key[:16], disk_key[16:]
        disk_key = aes_cipher.decrypt(disk_key, iv=iv)
        logging.debug("Disk Encryption Key (unencrypted) is {}".format(disk_key.hex()))

        logging.debug("Pairing complete.")

    with BluetoothCommunication() as bluetooth_interface:
        logging.debug("Begin connection")
        bluetooth_interface.accept()

        logging.debug("Generating session key")
        session_key = AES256KeyManager().create_key()
        aes_cipher = AES256Encryption(session_key)
        logging.debug("Encrypting session key with phone's public key")
        public_phone_cipher = RSAEncryption(RSA.import_key(phone_key))
        encrypted_session_key = public_phone_cipher.encrypt(session_key)
        logging.debug("Sending session key")
        bluetooth_interface.send(encrypted_session_key)

        logging.debug("Encrypting DEK(MEK)")
        dek_mek_tek = aes_cipher.encrypt(disk_key_mek)
        logging.debug("Sending IV || DEK(MEK)[TEK]")
        bluetooth_interface.send(aes_cipher.iv + dek_mek_tek)

        logging.debug("Receiving Disk Encryption Key (unencrypted)")
        disk_key = bluetooth_interface.receive(64)
        iv, disk_key = disk_key[:16], disk_key[16:]
        disk_key = aes_cipher.decrypt(disk_key, iv=iv)
        logging.debug("Disk Encryption Key (unencrypted) is {}".format(disk_key.hex()))

        logging.debug("Begin heartbeat phase")
        nonces = set()
        while True:
            logging.debug("Waiting for a nonce...")
            start = time.time()
            heartbeat = bluetooth_interface.receive()
            duration = time.time() - start
            logging.debug("Received heartbeat after {} seconds".format(duration))
            logging.debug("Decrypting heartbeat")
            iv, heartbeat = heartbeat[:16], heartbeat[16:]
            heartbeat = aes_cipher.decrypt(heartbeat, iv=iv)
            logging.debug("Received int: {}".format(int.from_bytes(heartbeat)))
            if heartbeat in nonces:
                logging.debug("*gasp* This number was used more than once!")
            nonces.add(heartbeat)

if __name__ == '__main__':
    main()
