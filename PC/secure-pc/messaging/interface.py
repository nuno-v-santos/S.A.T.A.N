from abc import ABCMeta, abstractmethod

class CommunicationInterface(metaclass=ABCMeta):

    @abstractmethod
    def connect(self, address) -> None:
        '''
        Connect to a peer at the given address.

        :param address: the address of the
                        peer you're connecting to
                        (protocol specific; for TCP
                         you might use IP and port,
                         for Bluetooth maybe a MAC
                         Address)
        '''
        raise NotImplementedError

    @abstractmethod
    def accept(self) -> None:
        '''
        Wait for a peer to connect.
        '''
        raise NotImplementedError

    @abstractmethod
    def send(self, msg: bytes) -> int:
        '''
        Send the specified message to the
        connected peer

        :param msg: the message to send
        :return: the number of bytes sent
        '''
        raise NotImplementedError

    @abstractmethod
    def receive(self, size: int) -> bytes:
        '''
        Receive a message from a peer

        :param size: max size of received message
        :return: the received message
        '''
        raise NotImplementedError
