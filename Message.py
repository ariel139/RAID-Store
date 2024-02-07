import socket
from struct import pack, unpack
from typing import Union
from enums import Category
import hashlib
class Message:
    def __init__(self, category: Category, opcode: int, data: Union[str, bytes,tuple], size:bytes = 0):
        # self.category = pack('H',socket.htons(category.value[0]))
        self.category = category.value
        self.opcode = opcode
        if isinstance(data, str):
           data = data.encode()
        if isinstance(data,bytes):
            self.data = self._get_params(data)       
        else:
            self.data = data
        if not size:

            self.size = Message._get_tuple_size(self.data)
            self.size = pack('H', socket.htons(self.size))
        else:
            self.size = size
    
    @staticmethod
    def _get_tuple_size(tup:tuple):
        size = 0
        for i in tup:
            size += len(i)+2
        return size
    @staticmethod
    def _parse_id(id: int): 
        id = socket.htons(id)
        return pack('I', id)
    
    @classmethod
    def parse_response(self,data:bytes):
        size = socket.ntohs(unpack('H',data[:2])[0])
        cat_op = data[2]
        opcode = cat_op & 15# not sure if mask needed ^ b'\xe0'
        catergory = (cat_op & 240) >> 5
        id = socket.ntohs(unpack('H', data[3:5])[0])
        params = self._get_params(data[5:])
        return Message(Category(catergory),opcode,params, size= size), id
    
    def _create_params(self,data:tuple)-> bytes:
        params = b''
        for obj in data:
            params+= len(obj).to_bytes(2,'little') + obj
        return params
    def _get_params(data: bytes)-> tuple:
        index = 0
        params = []
        while index < len(data):
            size = int.from_bytes(data[index:2],'little')
            param = data[index+2:index+2+size]
            params.append(param)
            index+=size
        return tuple(param)
    def build_message(self, id : Union[int, bytes]):
        if isinstance(id, int):
            id = self._parse_id(id)
        cat_op = (self.category << 5) | self.opcode
        cat_op = pack('c',cat_op.to_bytes(1,'big')) # dosent matter if ig or little beacuse one byte
        return self.size + cat_op + id + self._create_params(self.data)

    def __hash__(self) -> int:
        return hash(self)
