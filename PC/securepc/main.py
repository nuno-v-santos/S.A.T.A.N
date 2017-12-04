import logging
import qrcode
import time
import io
import wx

import ui.welcome
import ui.qr_code

#from messaging.communication import BluetoothCommunication, SecureCommunication
from security.keys import RSAKeyManager, AES256KeyManager, RSA
from security.encryption import RSAEncryption, AES256Encryption

from securepc.model import Model


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

        logging.debug("Receiving and decrypting session key")
        session_key = bluetooth_interface.receive(key_pair.public_key.size_in_bytes()) # Receive TEK
        logging.debug("Decrypting session key")
        session_key = rsa_private_cipher.decrypt(session_key)

        secure_interface = SecureCommunication(bluetooth_interface, key_pair.public_key)
        secure_interface.symmetric_key = session_key

        logging.debug("Receiving and decrypting phone's public key")
        phone_key = secure_interface.receive(480) # Receive IV | phone_public[TEK]
        logging.debug("Phone key is {}".format(phone_key))
        with io.BytesIO(phone_key) as f:
            phone_key = RSAKeyManager().load_key(f)

        logging.debug("Receiving and decrypting Disk Encryption Key (encrypted by Master Encryption Key)")
        disk_key_mek = secure_interface.receive(80) # receive IV | DEK(MEK)[TEK]
        logging.debug("Disk Encryption Key (MEK) is {}".format(disk_key_mek.hex()))

        logging.debug("Receiving and decrypting Disk Encryption Key (unencrypted)")
        disk_key = secure_interface.receive(64)
        logging.debug("Disk Encryption Key (unencrypted) is {}".format(disk_key.hex()))

        logging.debug("Pairing complete.")

    with BluetoothCommunication() as bluetooth_interface:
        logging.debug("Begin connection")
        secure_interface = SecureCommunication(bluetooth_interface, phone_key, generate=True)
        secure_interface.accept()


        logging.debug("Sending IV || DEK(MEK)[TEK]")
        secure_interface.send(disk_key_mek)

        logging.debug("Receiving and decrypting Disk Encryption Key (unencrypted)")
        disk_key = secure_interface.receive(64)
        logging.debug("Disk Encryption Key (unencrypted) is {}".format(disk_key.hex()))

        logging.debug("Begin heartbeat phase")
        nonces = set()
        while True:
            logging.debug("Waiting for a nonce...")
            start = time.time()
            heartbeat = secure_interface.receive()
            duration = time.time() - start
            logging.debug("Received heartbeat after {} seconds".format(duration))
            logging.debug("The value is: {}".format(int.from_bytes(heartbeat, 'big')))
            if heartbeat in nonces:
                logging.debug("*gasp* This number was used more than once!")
            nonces.add(heartbeat)


def main2():
    logging.getLogger().setLevel(logging.DEBUG)
    model = Model()
    app = wx.App()
    qr = qrcode.make("Never gonna give you up\nNever gonna let you down\nNever gonna turn around and desert you")
    welcome = ui.welcome.WelcomeDialog(None)
    dialog = ui.qr_code.QRDialog(qr, None)
    welcome.Show()
    dialog.Show()
    app.MainLoop()


if __name__ == '__main__':
    main2()
