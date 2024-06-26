"""
This class represents a message used for communication, with category, opcode, and data.

Attributes:
    category (Category): The category of the message.
    opcode (int): The opcode of the message.
    data (Union[bytes, tuple]): The data associated with the message.
    size (bytes): The size of the message.

Methods:
    __init__: Constructor method to initialize the message.
    _init_tup: Method to initialize the tuple data.
    _get_tuple_size: Static method to get the size of a tuple.
    _parse_id: Static method to parse an ID.
    parse_response: Class method to parse a response message.
    _create_params: Static method to create parameters.
    _get_params: Method to get parameters from bytes.
    build_message: Method to build a message.
    __repr__: Method to return a string representation of the message.
    __hash__: Method to compute the hash of the message.
    __eq__: Method to compare messages for equality.
"""

import socket
from struct import pack, unpack
from typing import Union
from enums import Category
from AES_manager import AESCipher
class Message:
    def __init__(self, category: Category, opcode: int, data: Union[bytes, tuple] = b'', size: bytes = 0,aes_key=None):
        """
        Constructor method to initialize the message.

        Args:
            category (Category): The category of the message.
            opcode (int): The opcode of the message.
            data (Union[bytes, tuple], optional): The data associated with the message. Defaults to b''.
            size (bytes, optional): The size of the message. Defaults to 0.
        """
        if aes_key is not None:
            self.aes_obj = AESCipher(aes_key)
        self.category = category.value
        self.opcode = opcode
        if isinstance(data, bytes):
            size = pack('I', socket.htonl(len(data) + 3))
            self.data = self._get_params(data)
        else:
            self.data = data
            self._init_tup()
        if not size:
            self.size = Message._get_tuple_size(self.data)
            self.size = pack('I', socket.htonl(self.size + 3))
        else:
            self.size = size

   
    def _init_tup(self):
        """
        Method to initialize the tuple data.
        """
        self.data = list(self.data)
        for i in range(len(self.data)):
            try:
                self.data[i] = self.data[i].encode()
            except Exception as err:
                if isinstance(self.data[i], bytes):
                    continue
                print(err)
                raise ValueError('The Values in the tuple must be str')
        self.data = tuple(self.data)

    @staticmethod
    def _get_tuple_size(tup: tuple):
        """
        Static method to get the size of a tuple.

        Args:
            tup (tuple): The input tuple.

        Returns:
            int: The size of the tuple.
        """
        size = 0
        for i in tup:
            size += len(i) + 4
        return size

    @staticmethod
    def _parse_id(id: int):
        """
        Static method to parse an ID.

        Args:
            id (int): The ID to parse.

        Returns:
            bytes: The parsed ID.
        """
        id = socket.htons(id)
        return pack('H', id)

    @classmethod
    def parse_response(cls, data: bytes):
        """
        Class method to parse a response message.

        Args:
            data (bytes): The message data.

        Returns:
            tuple: The parsed message and ID.
        """
        size = socket.ntohl(unpack('I', data[:4])[0]).to_bytes(4, 'big')
        cat_op = data[4]
        opcode = cat_op & 15
        category = (cat_op & 240) >> 5
        id = socket.ntohs(unpack('H', data[5:7])[0])
        params = cls._get_params(cls, data[7:])
        return Message(Category(category), opcode, params, size=size), id

    @staticmethod
    def _create_params(data: tuple) -> bytes:
        """
        Static method to create parameters.

        Args:
            data (tuple): The data to create parameters from.

        Returns:
            bytes: The created parameters.
        """
        params = b''
        for obj in data:
            params += len(obj).to_bytes(4, 'little') + obj
        return params

    def _get_params(self, data: bytes) -> tuple:
        """
        Method to get parameters from bytes.

        Args:
            data (bytes): The input data.

        Returns:
            tuple: The parameters.
        """
        index = 0
        params = []
        while index < len(data):
            size = int.from_bytes(data[index:index + 4], 'little')
            param = data[index + 4:index + 4 + size]
            params.append(param)
            index += size + 4
        return tuple(params)

    def build_message(self, id: Union[int, bytes]):
        """
        Method to build a message.

        Args:
            id (Union[int, bytes]): The ID of the message.

        Returns:
            bytes: The built message.
        """
        if isinstance(id, int):
            id = self._parse_id(id)
        cat_op = (self.category << 5) | self.opcode
        cat_op = pack('c', cat_op.to_bytes(1, 'little'))
        return self.size + cat_op + id + self._create_params(self.data)

    def __repr__(self) -> str:
        """
        Method to return a string representation of the message.

        Returns:
            str: String representation of the message.
        """        
        try:
            return f'Category {str(self.category)} opcode {str(self.opcode)}, data length: {len(self.data)}, message size {self.size}'+f'\ndata: {str(self.data)}'
        except Exception:
            return f'Category {str(self.category)} opcode {str(self.opcode)}, data length: {len(self.data)}, message size {self.size}'


    def __hash__(self) -> int:
        """
        Method to compute the hash of the message.

        Returns:
            int: The hash value.
        """
        return hash(self)

    def __eq__(self, other: object) -> bool:
        """
        Method to compare messages for equality.

        Args:
            other (object): Another message.

        Returns:
            bool: True if equal, False otherwise.
        """
        return self.__dir__ == other.__dir__
