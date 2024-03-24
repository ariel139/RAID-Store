import socket
from Message import Message
from struct import  unpack
class Node:
    MAX_RECIVE_SIZE = 1024
    SIZE_HEADER_SIZE = 2
    def __init__(self,soc: socket.socket):
        self.soc = soc
        self._debug = True
        self.messages = {}
        self._data_stream = b''
        

    def _generate_id(self):
        for i in range(2**16-1):
            if not str(i) in self.messages.keys():
                return i
        raise Exception('Unable to communicate to many sessions open')                
        
    
    def send(self, message: Message, id:int = 0):
        if id == 0:
            id = self._generate_id()
        else:
            self.messages.pop(id)
        message_data = message.build_message(id)
        self.soc.sendall(message_data)
        if self._debug:
            print('---DEBUG--- SENT:')
            print(message_data)
        self.messages[id] = message
        return id
    
    @staticmethod
    def _get_size(data_stream: bytes):
        size = data_stream[:2]
        size = unpack('H', size)[0]
        return socket.ntohs(size)
    
    def recive(self,) -> tuple:
        if self._data_stream != b'':
            header_size = self._data_stream
        else:
            header_size = self.soc.recv(Node.SIZE_HEADER_SIZE)
            while len(header_size) < Node.SIZE_HEADER_SIZE:
                header_size+= self.soc.recv(Node.SIZE_HEADER_SIZE)
        data = header_size
        int_size = self._get_size(header_size)
        while len(data) < int_size+Node.SIZE_HEADER_SIZE:
            data += self.soc.recv(Node.MAX_RECIVE_SIZE)
        if len(data) > int_size+Node.SIZE_HEADER_SIZE:
            self._data_stream += data[int_size:]
        
        message, id =  Message.parse_response(data)
        if id in self.messages:
            self.messages.pop(id)
        else:
            self.messages[id] = message
        return  message, id