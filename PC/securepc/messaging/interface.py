from abc import ABCMeta, abstractmethod
from typing import Tuple


class CommunicationInterface(metaclass=ABCMeta):
    @abstractmethod
    def connect(self, address) -> None:
        """
        Connect to a peer at the given address.

        :param address: the address of the
                        peer you're connecting to
                        (protocol specific; for TCP
                         you might use IP and port,
                         for Bluetooth maybe a MAC
                         Address)
        """
        raise NotImplementedError

    @abstractmethod
    def accept(self) -> None:
        """
        Wait for a peer to connect.
        """
        raise NotImplementedError

    @abstractmethod
    def send(self, msg: bytes) -> int:
        """
        Send the specified message to the
        connected peer

        :param msg: the message to send
        :throw: TimeoutException if timeout has been set and is exceeded
        :return: the number of bytes sent
        """
        raise NotImplementedError

    @abstractmethod
    def receive(self, size: int) -> bytes:
        """
        Receive a message from a peer

        :param size: max size of received message
        :throw: TimeoutException if timeout has been set and is exceeded
        :return: the received message
        """
        raise NotImplementedError

    @abstractmethod
    def get_client_info(self) -> Tuple[str, str]:
        """
        :return: A tuple containing a textual representation
                 of the client's name and address, in that order
        """
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        """
        Cleanup any resources
        """
        raise NotImplementedError

    @abstractmethod
    def set_timeout(self, timeout: int) -> None:
        """
        Set a timeout for this socket
        :param timeout: the timeout value, in seconds
        """
        raise NotImplementedError
