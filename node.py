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
        cnt = 1
        for i in self.messages.keys():
            if cnt >= 2 ** 16 -1:
                raise Exception('Unable to communicate to many sessions open')                
            if int(i) != cnt:
                return str(cnt)
            cnt+=1
    
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
    
    @staticmethod
    def _get_size(data_stream: bytes):
        size = data_stream[:2]
        size = socket.ntohs(size)
        return unpack('B', size)
    
    def recive(self,) -> Message:
        if self._data_stream != b'':
            header_size = self._data_stream
        else:
            header_size = self.soc.recv(Node.SIZE_HEADER_SIZE)
        while len(header_size) < Node.SIZE_HEADER_SIZE:
            header_size+= self.soc.recv(Node.SIZE_HEADER_SIZE)
        data = header_size
        int_size = self._get_size(header_size)
        while len(data) < int_size:
            data += self.soc.recv(Node.MAX_RECIVE_SIZE)
        if len(data) > int_size:
            self._data_stream += data[int_size:]
        
        message, id =  Message.parse_response(data)
        self.messages[id] = message