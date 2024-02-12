from enums import Requests
import app.gui_Exceptions
from socket import htonl, ntohl
from struct import pack, unpack
class Request:
    def __init__(self, request_type: Requests, file_name:str, **kwargs) -> None:
        if request_type == Requests.Add:
            if 'data' not in kwargs.keys():
                raise app.gui_Exceptions.NoDataInRequest()
            self.data = kwargs['data']
        self.file_name = file_name
        self.method = request_type
    
    def build_req(self) -> str:
        req_method = str(self.method.value).encode()
        file_name = self.file_name.encode()
        full_size = len(req_method)+len(file_name)+2
        if self.method == Requests.Add:
            full_size += len(self.data)+1 #16,384 GB limit
        full_size = htonl(full_size)
        full_size = pack('Q',full_size)
        messge = full_size +b'*'+req_method+b'*'+file_name
        if self.method == Requests.Add:
            messge+=self.data
        return messge
    
    def analyze_request(self,request:bytes):
        size = request[:8]
        
        method = Requests(int(request[8:9].decode()))
        file_name = 