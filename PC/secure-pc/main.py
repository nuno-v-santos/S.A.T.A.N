import logging

from Cryptodome.PublicKey import RSA

from messaging.communication import BluetoothCommunication


def main():
    # app = wx.App()
    # c = Controller()
    # app.MainLoop()
    logging.getLogger().setLevel(logging.DEBUG)
    key = RSA.generate(2048).publickey().exportKey()
    logging.debug("Starting bluetooth interface...")
    with BluetoothCommunication() as bluetooth_interface:
        bluetooth_interface.accept()
        logging.debug("Receiving message...")
        logging.debug(bluetooth_interface.receive(4096))
        msg = key
        bluetooth_interface.send(msg)


if __name__ == '__main__':
    main()
