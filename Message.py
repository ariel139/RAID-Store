import socket
from struct import pack, unpack
from typing import Union
from enums import Category
class Message:
    def __init__(self, category: Category, opcode: int, data: Union[bytes,tuple]=b'', size:bytes = 0):
        # self.category = pack('H',socket.htons(category.value[0]))
        self.category = category.value
        self.opcode = opcode
        if isinstance(data,bytes):
            size = pack('H',socket.htons(len(data) + 3))
            self.data = self._get_params(data)       
        else:
            self.data = data
            self._init_tup()
        if not size:
            self.size = Message._get_tuple_size(self.data)
            self.size = pack('H', socket.htons(self.size+3))
        else:
            self.size = size
    
    def _init_tup(self):
        self.data = list(self.data)
        for i in range(len(self.data)):
            try:
                self.data[i] = self.data[i].encode()
            except Exception as err:
                if isinstance(self.data[i],bytes):
                    continue
                print(err)
                raise ValueError('The Values in the tuple must be str')
        self.data = tuple(self.data)

    @staticmethod
    def _get_tuple_size(tup:tuple):
        size = 0
        for i in tup:
            size += len(i)+2
        return size
    @staticmethod
    def _parse_id(id: int): 
        id = socket.htons(id)
        return pack('H', id)
    
    @classmethod
    def parse_response(self,data:bytes):
        size = socket.ntohs(unpack('H',data[:2])[0]).to_bytes(2,'big')
        cat_op = data[2]
        opcode = cat_op & 15# not sure if mask needed ^ b'\xe0'
        catergory = (cat_op & 240) >> 5
        id = socket.ntohs(unpack('H', data[3:5])[0])
        params = self._get_params(self, data[5:])
        return Message(Category(catergory),opcode,params, size= size), id
    
    @staticmethod
    def _create_params(data:tuple)-> bytes:
        params = b''
        for obj in data:
            params+= len(obj).to_bytes(2,'little') + obj
        return params
    def _get_params(self,data: bytes)-> tuple:
        index = 0
        params = []
        while index < len(data):
            size = int.from_bytes(data[index:index+2],'little')
            param = data[index+2:index+2+size]
            params.append(param)
            index+=size+2
        return tuple(params)
    def build_message(self, id : Union[int, bytes]):
        if isinstance(id, int):
            id = self._parse_id(id)
        cat_op = (self.category << 5) | self.opcode
        cat_op = pack('c',cat_op.to_bytes(1,'little')) # dosent matter if ig or little beacuse one byte
        return self.size + cat_op + id + self._create_params(self.data)

    def __hash__(self) -> int:
        return hash(self)
    
    def __eq__(self, other: object) -> bool:
        return self.__dir__ == other.__dir__
