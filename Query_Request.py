from enums import Requests
from socket import htonl, ntohl, htons, ntohs
from struct import pack, unpack
from SharedMemory import SharedMemory
from Semaphore import Semaphore
SPLITER = b'*'
DEFAULT_SIZE = 2**(4*8)-1
class InvalidParameterError(Exception):
    pass
class Query_Request:
    def __init__(self, request_type: Requests, file_name:str,memory_view: SharedMemory = None, **kwargs) -> None:
        if 'data' in kwargs.keys():
            self.data = kwargs['data']
        else:
            self.data = b''
        self.file_name = file_name
        self.method = request_type
        if memory_view is not None:
            self.memory = memory_view
        else:
            self.memory =  SharedMemory(file_name,DEFAULT_SIZE)
    
    def build_req(self, write_to_mem = True) -> str:
        req_method = str(self.method.value).encode()
        file_name = self.file_name.encode()
        full_size = len(req_method)+len(file_name)+2
        if self.data !=b'':
            full_size += len(self.data)+1 #64kB limit | 2 bytes
        full_size = htonl(full_size)
        full_size = pack('I',full_size) #64 kb max| 2 bytes
        messge = full_size +b'*'+req_method+b'*'+file_name
        if self.data != b'':
            messge+=b'*'+self.data
        if write_to_mem:
            self.memory.write(messge)
        return messge
    
    def _get_size(byte_stream:bytes):
        size = byte_stream[:4]
        full_size = unpack('I',size)[0] #64 kb max
        return ntohl(full_size)
    
    @staticmethod
    def _get_request_stream(memory: SharedMemory):
        size = memory.read(4)
        cnt=0
        while size == b'\x00\x00\x00\x00':
            size = memory.read(4)
            if cnt>= memory.size:
                raise ValueError('No data in the buffer')
            cnt+=4
        int_size = Query_Request._get_size(size)
        data = memory.read(int_size)
        return size + data
    # index = 0
    # size= self.memory[index:index+2]
    # while size == b'\x00\x00':
    #     index+=2
    #     read_index = index % len(self.memory)
    #     size= self.memory[read_index:read_index+2]
    #     if index == len(self.memory):
    #         raise ValueError('There is no request in the buffer')
    # int_size = Request._get_size(size)
    # if int_size > self.memory.size:
    #     raise ValueError(f'Size of request is to high. got {int_size} need below {self.memory.size}')
    # read_index = index % len(self.memory)
    # if int_size+read_index-2 < self.memory.size:
    #     req_stream = self.memory[read_index+2: int_size+read_index+2]
    #     self.memory[read_index+2: int_size+read_index+2]  = bytes(int_size)
    #     return req_stream
    # req_stram =self.memory[read_index+2:]
    # got  =len(self.memory)-read_index-2
    # self.memory[read_index:] = bytes(got)
    # req_stram+= self.memory[:int_size-got]
    # self.memory[:int_size-got] = bytes(len(self.memory)- (int_size-got))
    #     return req_stram
    @staticmethod
    def analyze_request(memory_view:SharedMemory):
        request = Query_Request._get_request_stream(memory_view)
        fields =[]
        index = 0
        for _ in range(4):
            f_index = request.find(SPLITER, index)
            if f_index == -1:
                fields.append(request[index:])
                break
            elif len(fields)>=3:
                fields.append(request[index:])
                break
            fields.append(request[index:f_index])
            index = f_index+1
        method = Requests(int(fields[1].decode()))
        file_name = fields[2].decode()
        if method == Requests.Add:
            data = fields[3]
        else:
            data = b''
        return Query_Request(method,file_name,data=data)
    
