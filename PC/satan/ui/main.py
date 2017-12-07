import subprocess
import tempfile
import qrcode
import sys
import os
import io

from pubsub import pub
from getpass import getpass

from satan import application
from satan.util import async_publish
try:
    from satan.ui.completion import init_completion
except ImportError: # Windows does not have the readline library, there will be no completion
    def init_completion():
        pass
from satan.constants import APP_NAME, APP_VERBOSE_NAME
from satan.security.keys import RSAKeyManager
from satan.constants import CONFIG_DIRECTORY


class MainUI(object):
    def __init__(self):
        self.app = application.get_instance()
        self.connected = False
        self.encrypted = True
        self.running = True

    def start(self):
        print("Welcome to {}.".format(APP_VERBOSE_NAME))
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

    def show_image(self, path: str):
        """
        Show an image using the default image viewer.

        :param path: path to the image file
        """
        if sys.platform in ('linux', 'linux2'):
            subprocess.Popen(['xdg-open', path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif sys.platform == 'win32':
            subprocess.Popen(['powershell', '-c', path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def welcome(self):
        print("It seems this is your first time running this program.")
        print("First, you will need to set a password.")
        while True:
            password = getpass("Enter password: ")
            check = getpass("Retype password: ")
            if password.strip() == '':
                print("The password can't be empty")
                continue
            if password == check:
                break
            print("Wrong password! Please try again.")
        self.app.define_password(password)
        print("Great! Please open the app on your smartphone, then press Return.")
        input("")
        print('Press "Pairing" on your phone, then select your computer from the list.')
        print("Waiting for pairing process to complete...")
        self.app.accept_connection()

        with io.BytesIO() as f:
            RSAKeyManager().store_key(self.app.public_key, f)
            public_key = f.getvalue()

        print("A QR Code will be displayed on your screen.")
        print("Please scan it with your phone, then close the image.")
        print("Press Return to display the QR")
        input("")

        qr = qrcode.make(public_key)
        qr.format = 'PNG'
        qr_fd, qr_path = tempfile.mkstemp('.png')
        os.close(qr_fd)
        with open(qr_path, 'wb') as f:
            qr.save(f)
        self.show_image(qr_path)

        input("Press Return after you read the QR")
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
        if not self.connected:
            self.connected = True
            print('Phone has connected')

    def handle_disconnect(self):
        if self.connected:
            self.connected = False
            print('Phone has disconnected')

    def handle_bad_nonce(self):
        print("Potential attack detected! Shutting down")
        self.exit()

    def handle_encrypted(self):
        if not self.encrypted:
            print("Files have been encrypted")
            self.encrypted = True

    def handle_decrypted(self):
        if self.encrypted:
            self.encrypted = False
            print("Files have been decrypted")

    def print_instructions(self):
        print("----------------------------------")
        print("Valid commands:")
        print("add <file> - Adds a file to the list of encrypted files (only works when connected to the phone)")
        print("remove <file> - Remove a file from the list of encrypted files " +
              "(only works when connected to the phone)")
        print("status - Print current status")
        print("exit - Exit the program")
        print("----------------------------------")

    def repl(self):
        """
        Read Eval Print Loop

        Process the user's input and redirect it to the application
        """
        self.print_instructions()
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
                    print("Warning: not connected. Removing a file would leave it encrypted. Ignoring...")
            elif cmd == 'status':
                self.print_status()
            elif cmd == 'unpair':
                if self.encrypted:
                    print("Warning: unpairing right now would keep your files encrypted. Please" +
                          " connect to your phone first")
                    continue
                print("Press done on your phone app")
                self.app.unpair()
                self.exit()
            elif cmd == 'exit':
                self.exit()
            else:
                print("Invalid command.")
                self.print_instructions()

    def exit(self):
        self.running = False
        print("Exiting, please wait...")
        self.app.exit()

    def remove_files(self, args):
        for path in args:
            if self.app.remove_file(path):
                print("{} removed.".format(path))
            else:
                print("{} could not be removed.".format(path))

    def add_files(self, paths):
        for path in paths:
            if self.app.add_file(path):
                print("{} added.".format(path))
            else:
                print("{} could not be added.".format(path))

    def print_status(self):
        print("Connection: {}".format("Connected" if self.connected else "Not connected"))
        print("Encryption: {}".format("Encrypted" if self.encrypted else "Decrypted"))
        print("Protected files:")
        for file in self.app.files:
            print("\t{}".format(file))
