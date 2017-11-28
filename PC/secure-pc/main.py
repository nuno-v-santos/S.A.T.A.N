import wx
from .controller import Controller
from .communication import BluetoothInterface
from Cryptodome.PublicKey import RSA
import qrcode

def main():
    # app = wx.App()
    # c = Controller()
    # app.MainLoop()
    key = RSA.generate(2048).publickey().exportKey();
    print("Starting bluetooth interface...")
    bluetooth_interface = BluetoothInterface()
    bluetooth_interface.accept_connection()
    print("Receiving message...")
    print(bluetooth_interface.receive())
    msg = key
    print('Sending {}'.format(msg))
    bluetooth_interface.send(msg)
    bluetooth_interface.close()


if __name__ == '__main__':
    main()
