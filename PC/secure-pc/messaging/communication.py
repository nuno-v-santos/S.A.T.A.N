from .interface import CommunicationInterface
from .constants import uuid
import bluetooth
import logging


class BluetoothCommunication(CommunicationInterface):
    def __init__(self):
        self.logger = logging.getLogger('communication')
        self.socket = None
        self.server_socket = None

    def accept(self):
        self.server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.server_socket.bind(("", bluetooth.PORT_ANY))
        self.server_socket.listen(1)
        self.port = self.server_socket.getsockname()[1]

        bluetooth.advertise_service(self.server_socket, "SecurePC",
                                    service_id=uuid,
                                    service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
                                    profiles=[bluetooth.SERIAL_PORT_PROFILE]
                                    )
        self.logger.debug("Waiting for connection on RFCOMM port {}".format(self.port))
        self.socket, self.client_info = self.server_socket.accept()
        self.logger.debug("Accepted connection from {}".format(self.client_info))

    def connect(self, address):
        self.logger.debug('Connecting to {}'.format(address))

        service_matches = bluetooth.find_service(uuid=uuid, address=address)
        # FIXME
        assert len(service_matches) > 0, "No service on address {}".format(address)

        first_match = service_matches[0]
        name, host, port = first_match['name'], first_match['host'], first_match['port']
        self.logger.debug('Found service running on {name} at {host}, port {port}'.format(
            name=name,
            host=host,
            port=port
        ))
        self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.socket.connect((host, port))
        self.logger.debug('Connected')

    def receive(self, size=1024):
        self.logger.debug('Receiving message of max size {}'.format(size))
        return self.socket.recv(size)

    def send(self, msg):
        self.logger.debug('Sending {}'.format(msg))
        return self.socket.send(msg)

    def close(self):
        self.logger.debug('Closing BluetoothCommunication')

        if self.socket is not None:
            self.logger.debug('Closing socket')
            self.socket.close()

        if self.server_socket is not None:
            self.logger.debug('Closing server socket')
            self.server_socket.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
