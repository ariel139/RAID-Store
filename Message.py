import socket
from struct import pack, unpack
from typing import Union
class Message:
    def __init__(self, category: bytes, opcode: bytes, data: Union[str, bytes], size = 0):
        self.category = socket.htons(pack('B',category))
        self.opcode = socket.htons(pack('B', opcode))
        if isinstance(data, str):
            self.data = data.encode()
        self.data = self._parse_data(data)
        if not size:
            self.size = len(self.data)
            self.size = socket.htonl(pack('I', self.size))
        else:
            self.size = size
    
    @staticmethod
    def _parse_data(data:bytes, send = True) -> bytes:
        method = (socket.htonl, socket.htons) if send else  (socket.ntohs, socket.ntohl)
        reminder = len(data) % 2
        parsed = b''
        for i in range(0,len(data)-reminder-2,2):
            parsed += method[0](data[i:i+2])
        if reminder:
            parsed += method[1](data[-1])
        return parsed
    
    @staticmethod
    def _parse_id(id: int): 
        id = socket.htons(id)
        return pack('I', id)
    
    @classmethod
    def parse_response(self,data:bytes):
        size = socket.ntohs(unpack('H',data[:2])[0])
        catergory = socket.ntohs(unpack('B',data[2:3])[0]) # not sure if mask needed ^ b'\xe0'
        opcode = socket.ntohs(unpack('B', data[2:3])[0]) # not sure if mask needed^ b'\x1f'
        id = socket.ntohs(unpack('H', data[3:5])[0])
        data = Message._parse_data(data[5:], send = False)
        return Message(catergory,opcode,data, size= size), id

    def build_message(self, id : Union[int, bytes]):
        if isinstance(id, int):
            id = self._parse_id(id)
        return self.size + self.category + self.opcode + id + self.data


message = b'\x13\x44\x54\xf5\x55\x34\x65'
msg = Message.parse_response(message)