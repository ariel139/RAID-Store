"""
This class represents a node in a network, responsible for sending and receiving messages.

Attributes:
    MAX_RECIVE_SIZE (int): Maximum receive size for messages.
    SIZE_HEADER_SIZE (int): Size of the header.
    soc (socket.socket): The socket associated with the node.
    _debug (bool): Debug flag.
    messages (dict): Dictionary of messages.
    _data_stream (bytes): Data stream.

Methods:
    __init__: Constructor method to initialize the node.
    _generate_id: Method to generate a unique ID for a message.
    send: Method to send a message.
    _get_size: Static method to get the size of the data.
    recive: Method to receive a message.
"""

import socket
from Message import Message
from struct import unpack, pack
from RSA_communication import *
from AES_manager import AESCipher
class Node:
    MAX_RECIVE_SIZE = 1024
    SIZE_HEADER_SIZE = 4

    def __init__(self, soc: socket.socket,rsa_comm:bool=True,**args):
        """
        Constructor method to initialize the node.

        Args:
            soc (socket.socket): The socket associated with the node.
        """
        self.soc = soc
        self._debug = True
        self.messages = {}
        self._data_stream = b''
        if rsa_comm:
            self.rsa_comm = True
            comm_type = args['comm_type']
            self.rsa_key = self.init_rsa_communication(comm_type)
    
    def init_rsa_communication(self,comm_type: CommunicatorType):
        if comm_type == CommunicatorType.RECIVER:
            self.rsa = RSACommunication(CommunicatorType.RECIVER)
        elif comm_type == CommunicatorType.SENDER:
            self.rsa = RSACommunication(CommunicatorType.SENDER)
        return self.rsa.auto_soc(self.soc).decode()

    def _generate_id(self):
        """
        Method to generate a unique ID for a message.

        Returns:
            int: The generated ID.
        
        Raises:
            Exception: If unable to communicate due to too many open sessions.
        """
        for i in range(2**16 - 1):
            if not str(i) in self.messages.keys():
                return i
        raise Exception('Unable to communicate too many sessions open')

    def encode_data_stream(self,data:bytes):
        aes_obj = AESCipher(self.rsa_key)
        encrypted = aes_obj.encrypt(data)
        size = len(encrypted)
        n_size = socket.htonl(size)
        packed_size = pack('I',n_size)
        return packed_size+encrypted
    def send(self, message: Message, id: int = 0):
        """
        Method to send a message.

        Args:
            message (Message): The message to send.
            id (int, optional): The ID of the message. Defaults to 0.

        Returns:
            int: The ID of the sent message.
        """
        if message is None:
            print(f'Message with ID: {id} did not sent because of None')
            return
        if id == 0:
            id = self._generate_id()
        else:
            self.messages.pop(id)
        message_data = message.build_message(id)
        if self.rsa_comm:
            message_data = self.encode_data_stream(message_data)
        self.soc.sendall(message_data)
        if self._debug:
            print('---DEBUG--- SENT:')
            try:
                print(message)
            except Exception:
                print('could not print')
        self.messages[id] = message
        return id

    @staticmethod
    def _get_size(data_stream: bytes):
        """
        Static method to get the size of the data.

        Args:
            data_stream (bytes): The data stream.

        Returns:
            int: The size of the data.
        """
        size = data_stream[:4]
        size = unpack('I', size)[0]
        return socket.ntohl(size)
    def decode_rsa(self, data):
        # size = unpack('I',data[:4])
        # size = socket.ntohl(bytes[:4])
        aes_obj = AESCipher(self.rsa_key)
        return aes_obj.decrypt(data[4:])

    def recive(self) -> tuple:
        """
        Method to receive a message.

        Returns:
            tuple: The received message and ID.
        """
        if self._data_stream != b'':
            header_size = self._data_stream
        else:
            header_size = self.soc.recv(Node.SIZE_HEADER_SIZE)
            while len(header_size) < Node.SIZE_HEADER_SIZE:
                header_size += self.soc.recv(Node.SIZE_HEADER_SIZE)
        data = header_size
        int_size = self._get_size(header_size)
        while len(data) < int_size + Node.SIZE_HEADER_SIZE:
            data += self.soc.recv(Node.MAX_RECIVE_SIZE)
        if len(data) > int_size + Node.SIZE_HEADER_SIZE:
            self._data_stream += data[int_size + Node.SIZE_HEADER_SIZE:]
        #TODO: decode rSA
        if self.rsa_comm:   
            data = self.decode_rsa(data)
        message, id = Message.parse_response(data)
        if self._debug:
            try:
                print('---RECIVED---:')
                print(message)
            except Exception:
                print('could not print data recived')
        if id in self.messages:
            self.messages.pop(id)
        else:
            self.messages[id] = message
        return message, id
