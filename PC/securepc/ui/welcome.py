import logging
import qrcode
import io

from getpass import getpass
from securepc import application
from securepc.security.keys import RSAKeyManager


def welcome():
    app = application.get_instance()
    print("It seems this is your first time running this program.")
    print("Welcome! First, you will need to set a password.")
    while True:
        password = getpass("Enter password: ")
        check = getpass("Retype password: ")
        if password == check:
            break
        print("Wrong password! Please try again.")
    app.define_password(password)
    print("Great! Please open the app on your smartphone, then press Return.")
    input("")
    print('Press "Pairing" on your phone, then select your computer from the list.')
    print("Waiting for pairing process to complete...")
    app.accept_connection()
    print("I've accepted a connection from {name} @ {address}.".format(
        name=app.phone_name,
        address=app.phone_address
    ))
    print("Is this correct? If not, please terminate the application and try again.")
    print("Otherwise, press Return.")
    input("")
    logging.debug("Creating QR Code with public key")
    with io.BytesIO() as f:
        RSAKeyManager().store_key(app.public_key, f)
        public_key = f.getvalue()
    qr = qrcode.make(public_key)
    print("When you press Return, a QR Code will be displayed on your screen.")
    print("Please scan it with your phone, then close the image.")
    qr.show()
    app.initial_exchange()
    print("Phone has been successfully paired.")

