import threading

from pubsub import pub

def async_publish(*args, **kwargs):
    async_callback = lambda: pub.sendMessage(*args, **kwargs)
    thread = threading.Thread(target=async_callback)
    thread.start()
