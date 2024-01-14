import socket
from typing import Union, Tuple
from threading import Thread
from struct import pack, unpack
from random import choice
# global vars
running = True


def analyze_message(data: bytes):
    pass

def handle_message(data: tuple):
    pass

def handle_client(client_soc: socket.socket):
    while True:
        data = 



def main(creds: Tuple(str, int )):
    global running
    server_socket = socket.socket()
    server_socket.bind(creds)
    server_socket.listen(5)
    while running:
        addr, soc = server_socket.accept()
        print('new connection from: '+addr)
        threads = []
        th = Thread(target=handle_client, args= (soc,))
        th.start()
        threads.append(th)

class Message:
    def __init__(self, category: bytes, opcode: bytes, data: Union(str, bytes), size = 0):
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
    def parse_response(data:bytes):
        id = socket.ntohs(unpack('B',data[:2]))
        catergory = socket.ntohs(unpack('B',data[2:3] )) # not sure if mask needed ^ b'\xe0'
        opcode = socket.ntohs(unpack('B', data[2:3])) # not sure if mask needed^ b'\x1f'
        size = socket.htonl(unpack('I', data[3:5]))
        data = Message._parse_data(data[5:], send = False)
        return Message(catergory,opcode,data, size= size), id

    def build_message(self, id : Union(int, bytes)):
        if isinstance(id, int):
            id = self._parse_id(id)
        return id + self.category + self.opcode + self.size + self.data

        
    
class node:
    def __init__(self,soc: socket.socket):
        self.soc = soc
        self._debug = True
        self.messages = {}

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
    
    def recive(message_data: bytes):
        id, message: Message = Message.parse_response(message_data)
        
        # try printing the type of id
        
            

            

         

if __name__ == "__main__":
    main()