from DataBaseSession import DataBaseSession
from pathlib import Path
from uuid import getnode
from hashlib import sha256
MAC= hex(getnode()).encode()
class Data(DataBaseSession):
    GET_FIELD_QUERY = 'FROM Data SELECT * WHERE id=%s;'
    INSERT_FILED = 'INSERT INTO Data VALUES %s,%s,%s,%s,%s,%s,%s,%s;'
    def __init__(self,id_num:int):
        super().__init__()
        data_field = self.fetch((Data.GET_FIELD_QUERY,(id_num)))
        self.hash_value = data_field[0]
        self.id_num = id_num
        self.size = data_field[2]
        self.path = data_field[3]
        self.relation = data_field[4]
        self.location = data_field[5]
        self.parity = data_field[6]
        self.drive = data_field[7]
    
    def CreateField(self,path: str, user_id:str, drive:int,file_hash: bytes= b'', mac:bytes = MAC, ):
        file_data = self._get_file_data(path)
        if file_hash == b'':
            file_hash = sha256(file_data).hexdigest().encode()
        size = len(file_data)
        parity = False
        self.insert(Data.INSERT_FILED,(file_hash,size,path,user_id,drive,parity))
        rec_id = self._get_latest_record_id()
        return Data(rec_id)
    def _get_latest_record_id(self,):
        # you may also use LAST_INSERT_ID()
        query = 'SELECT MAX(id) FROM Data'
        id_num = self.fetch(query)
        return id_num
    def _get_file_data(self, file_path):
        file_path = Path(file_path)
        with open(file_path,'rb') as file:
            return file.read()

    