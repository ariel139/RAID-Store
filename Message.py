import socket
from struct import pack, unpack
from typing import Union
from enums import Category
class Message:
    def __init__(self, category: Category, opcode: int, data: Union[str, bytes,tuple], size = 0):
        # self.category = pack('H',socket.htons(category.value[0]))
        self.category = category.value
        self.opcode = opcode
        if isinstance(data, tuple):
            self.data = self._create_params(data)
        elif isinstance(data, str):
           self.data = data.encode()
        else:
            self.data = data
        if not size:
            self.size = len(self.data)
            self.size = pack('H', socket.htons(self.size))
        else:
            self.size = size
    
   
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
        return Message(Category(catergory),opcode,data, size= size), id
    
    def _create_params(self,data:tuple):
        params = b''
        for obj in data:
            params+= len(obj).to_bytes(2,'little') + obj
        return params
    def _get_params(data: bytes):
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
        return self.size + cat_op + id + self.data



msg_sent = Message(Category.Authentication,1,b"\x5\xhello\x3123\x14")
msg_data = msg_sent.build_message(1)
msg_recv = Message.parse_response(msg_data)