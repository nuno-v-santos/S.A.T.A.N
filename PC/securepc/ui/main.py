from pubsub import pub

from securepc import application
from securepc.util import async_publish
from securepc.ui.completion import init_completion

class MainUI(object):
    def __init__(self):
        self.app = application.get_instance()
        self.connected = False
        self.encrypted = True

        init_completion()
        async_publish('app_start')
        pub.subscribe(self.handle_connect, 'connected')
        pub.subscribe(self.handle_disconnect, 'disconnected')
        self.repl()

    def handle_connect(self):
        self.connected = True
        print('Phone has connected')

    def handle_disconnect(self):
        self.connected = False
        print('Phone has disconnected')

    def repl(self):
        while True:
            print('All work and no play makes Jack a dull boy')
            __import__('time').sleep(1)
