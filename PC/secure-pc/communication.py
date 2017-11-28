import bluetooth


class BluetoothInterface(object):
    def __init__(self):
        socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        socket.bind(("", bluetooth.PORT_ANY))
        socket.listen(1)

        uuid = "7e32b920-c98b-11e7-8f1a-0800200c9a66"
        bluetooth.advertise_service(socket, "SecurePC",
                                    service_id=uuid,
                                    service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
                                    profiles=[bluetooth.SERIAL_PORT_PROFILE]
                                    )
        self.socket = socket
        self.port = socket.getsockname()[1]

    def accept_connection(self):
        print("Waiting for connection on RFCOMM port {}".format(self.port))
        self.client_sock, self.client_info = self.socket.accept()
        print("Accepted connection from {}".format(self.client_info))

    def receive(self, bytes=1024):
        return self.client_sock.recv(bytes)

    def send(self, msg):
        return self.client_sock.send(msg)

    def close(self):
        self.client_sock.close()
        self.socket.close()
