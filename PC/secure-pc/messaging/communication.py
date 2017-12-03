from .interface import CommunicationInterface
from .constants import uuid
from ..security.keys import RSAKeyManager, AES256KeyManager, RSAKey, AESKey
from ..security.encryption import RSAEncryption, AES256Encryption
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


class SecureCommunication(CommunicationInterface):
    """
    This class serves to encapsulate a different communication
    class and encrypt/decrypt all messages except for the initial
    connection using a session key. The encryption used will be
    AES-256 with EAX mode.

    On the first connection, one of the peers is responsible
    for generating and sending a session key, encrypted with an RSA
    key using RSA-OAEP. From that point on, all messages will consist
    of a 16-byte IV, followed by the message itself, encrypted with
    the session key.

    After closing the connection, this object must not be reused;
    please create a new instance, encapsulating the same underlying
    interface if need be.
    """

    def __init__(self, communication: CommunicationInterface, key: RSAKey, generate: bool = False):
        """
        :param communication: The interface to encapsulate
        :param key: the asymmetric key to use in the initial pairing
        :param generate: if True, this object is responsible for generating the session key
        """
        self.communication: CommunicationInterface = communication
        self.generate: bool = generate

        self.symmetric_cipher: AES256Encryption = None
        self.asymmetric_cipher: RSAEncryption = RSAEncryption(key)

    @property
    def asymmetric_key(self) -> RSAKey:
        return self.asymmetric_cipher.key

    @asymmetric_key.setter
    def asymmetric_key(self, key: RSAKey) -> None:
        self.asymmetric_cipher = RSAEncryption(key)

    @property
    def symmetric_key(self) -> bytes:
        return self.symmetric_cipher.key

    @symmetric_key.setter
    def symmetric_key(self, key: AESKey) -> None:
        self.symmetric_cipher = AES256Encryption(key, mode=AES256Encryption.MODE_EAX)

    def _exchange_keys(self) -> None:
        """
        Exchange the session key encrypted through RSA-OAEP
        using a predetermined asymmetric key.

        :param key: the asymmetric key to use for the exchange
        """
        if self.generate:
            key_manager = AES256KeyManager()
            session_key = key_manager.create_key()
            encrypted_session_key = self.asymmetric_cipher.encrypt(session_key)
            self.communication.send(encrypted_session_key)
            self.symmetric_key = session_key
        else:
            encrypted_session_key = self.communication.receive(self.asymmetric_key.size_in_bytes())
            self.symmetric_key = self.asymmetric_cipher.decrypt(encrypted_session_key)

    def connect(self, address) -> None:
        """
        Connect to a peer and exchange a session key

        :param address: the address of the peer to connect to
        """
        self.communication.connect(address)
        self._exchange_keys()

    def accept(self) -> None:
        """
        Wait until a peer connects; then, exchange
        a session key
        """
        self.communication.accept()
        self._exchange_keys()

    def send(self, msg: bytes) -> int:
        encrypted = self.symmetric_cipher.encrypt(msg)
        return self.communication.send(encrypted)

    def receive(self, size: int) -> bytes:
        msg = self.communication.receive(size)
        decrypted = self.symmetric_cipher.decrypt(msg)
        return decrypted
