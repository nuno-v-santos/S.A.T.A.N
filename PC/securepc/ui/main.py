import logging
import qrcode
import sys
import io

from pubsub import pub
from getpass import getpass

from securepc import application
from securepc.util import async_publish
from securepc.ui.completion import init_completion
from securepc.constants import APP_NAME
from securepc.security.keys import RSAKeyManager
from securepc.constants import CONFIG_DIRECTORY


class MainUI(object):
    def __init__(self):
        self.app = application.get_instance()
        self.connected = False
        self.encrypted = True
        self.running = True

    def start(self):
        if not self.app.has_paired():
            self.welcome()
        else:
            self.authenticate()
            self.app.load_files_list()
            if self.app.ensure_encryption():
                print("Previous crash detected. Files were re-encrypted.")

        init_completion()
        pub.subscribe(self.handle_connect, 'connected')
        pub.subscribe(self.handle_disconnect, 'disconnected')
        pub.subscribe(self.handle_encrypted, 'encrypted')
        pub.subscribe(self.handle_decrypted, 'decrypted')
        pub.subscribe(self.handle_bad_nonce, 'bad_nonce')
        async_publish('app_start')
        self.repl()

    def welcome(self):
        print("It seems this is your first time running this program.")
        print("Welcome! First, you will need to set a password.")
        while True:
            password = getpass("Enter password: ")
            check = getpass("Retype password: ")
            if password == check:
                break
            print("Wrong password! Please try again.")
        self.app.define_password(password)
        print("Great! Please open the app on your smartphone, then press Return.")
        input("")
        print('Press "Pairing" on your phone, then select your computer from the list.')
        print("Waiting for pairing process to complete...")
        self.app.accept_connection()
        print("I've accepted a connection from {name} @ {address}.".format(
            name=self.app.phone_name,
            address=self.app.phone_address
        ))
        print("Is this correct? If not, please terminate the application and try again.")
        print("Otherwise, press Return.")
        input("")
        logging.debug("Creating QR Code with public key")

        with io.BytesIO() as f:
            RSAKeyManager().store_key(self.app.public_key, f)
            public_key = f.getvalue()
        qr = qrcode.make(public_key)

        print("When you press Return, a QR Code will be displayed on your screen.")
        print("Please scan it with your phone, then close the image.")
        qr.show()
        self.app.initial_exchange()
        print("Phone has been successfully paired.")
        print("Your configuration files are located in {}.".format(CONFIG_DIRECTORY))
        print("Please backup this directory whenever you make a change in the configuration.")
        print("If you don't, you might lose all your protected files if something happens.")

    def authenticate(self):
        for i in range(3):
            password = getpass("Enter password: ")
            if self.app.validate_password(password):
                break
        else:
            print("Failed after 3 attempts. Exiting...")
            sys.exit(1)

    def handle_connect(self):
        self.connected = True
        print('Phone has connected')

    def handle_disconnect(self):
        self.connected = False
        print('Phone has disconnected')

    def handle_bad_nonce(self):
        print("Potential attack detected! Shutting down")
        self.exit()

    def handle_encrypted(self):
        self.encrypted = True
        print("Files have been encrypted")

    def handle_decrypted(self):
        self.encrypted = False
        print("Files have been decrypted")

    def print_instructions(self):
        print("Valid commands:".format(APP_NAME))
        print("\tadd <file> - Adds a file to the list of encrypted files (only works when connected to the phone)")
        print("\tremove <file> - Remove a file from the list of encrypted files " +
              "(only works when connected to the phone)")
        print("\tstatus - Print current status")
        print("\texit - Exit the program")

    def repl(self):
        """
        Read Eval Print Loop

        Process the user's input and redirect it to the application
        """
        print("Welcome to {}.")
        while self.running:
            line = input().split()
            if not line:
                continue
            cmd = line[0]
            args = line[1:]
            if cmd == 'add':
                if self.connected:
                    self.add_files(args)
                else:
                    print("Can only add a protected file when connected.")
            elif cmd == 'remove':
                if self.connected:
                    self.remove_files(args)
                else:
                    print("Warning: not connected. Removing this file would leave it encrypted. Ignoring...")
            elif cmd == 'status':
                self.print_status()
            elif cmd == 'exit':
                self.exit()
            else:
                print("Invalid command.")

    def exit(self):
        self.running = False
        self.app.exit()

    def remove_files(self, args):
        for path in args:
            self.app.remove_file(path)

    def add_files(self, paths):
        for path in paths:
            self.app.add_file(path)

    def print_status(self):
        print("Connection: {}".format("Connected" if self.connected else "Not connected"))
        print("Encryption: {}".format("Encrypted" if self.encrypted else "Decrypted"))
        print("Protected files:")
        for file in self.app.files:
            print("\t{}".format(file))
