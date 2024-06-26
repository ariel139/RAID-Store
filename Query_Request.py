from enums import Requests
from socket import htonl, ntohl, htons, ntohs
from struct import pack, unpack
from SharedMemory import SharedMemory
from Semaphore import Semaphore
SPLITER = b'*'
DEFAULT_SIZE = 2**(4*7)-1 # based on page size 
class InvalidParameterError(Exception):
    pass
class Query_Request:
    USING_DATA_TUPLE = (Requests.Add_File, Requests.Response,Requests.Error, Requests.Info)
    def __init__(self, request_type: Requests, file_name:str= '',memory_view: SharedMemory = None, **kwargs) -> None:
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
        try:
            method = Requests(int(fields[1].decode()))
        except ValueError:
            print(fields)
        file_name = fields[2].decode()
        if method in Query_Request.USING_DATA_TUPLE:
            data = fields[3]
        else:
            data = b''
        return Query_Request(method,file_name,data=data)
    
if __name__ == "__main__":
    print('as')
    memory =  SharedMemory('ariel',DEFAULT_SIZE)