from DataBaseSession import DataBaseSession
from pathlib import Path
from uuid import getnode
from hashlib import sha256
MAC= hex(getnode()).encode()
class Data(DataBaseSession):
    GET_FIELD_QUERY = 'select * from data where id=%s;'
    INSERT_FILED_NOT_PATH = 'INSERT INTO data (hash,size,relation,location,parity) VALUES (%s,%s,%s,%s,%s);'
    INSERT_FILED = 'INSERT INTO Data VALUES %s,%s,%s,%s,%s,%s;'
    UPDATE_PATH_FILED = "UPDATE data SET `path`=%s WHERE `id`=%s"
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
    
    
    @classmethod
    def CreateField(path: str, user_id:str, drive:int,file_hash: bytes,size:int, parity:bool = False ):
        db_session = DataBaseSession()
        db_session.insert(Data.INSERT_FILED,(file_hash,size,path,user_id,drive,parity))
        rec_id = Data._get_latest_record_id()
        return Data(rec_id)
    
    @staticmethod
    def CreateFieldNoPath(user_id:str, drive:int,file_hash: bytes,size:int, parity:bool=False ):
        db_session = DataBaseSession()
        parity = 0 if not parity else 1
        db_session.insert(Data.INSERT_FILED_NOT_PATH,(file_hash,size,user_id,drive,parity))
        rec_id = Data._get_latest_record_id()
        return Data(rec_id)
    
    @staticmethod
    def update_path_filed(id: int, path:str):
        db_session = DataBaseSession()
        db_session.insert(Data.UPDATE_PATH_FILED,(path,id))

    
    @staticmethod
    def _get_latest_record_id():
        # you may also use LAST_INSERT_ID()
        db_session = DataBaseSession()
        query = 'SELECT MAX(id) FROM Data'
        id_num = db_session.fetch(query)
        return id_num
    
    def _get_file_data(self, file_path):
        file_path = Path(file_path)
        with open(file_path,'rb') as file:
            return file.read()

if __name__ == "__main__":
    # Data.CreateFieldNoPath('ariel0', 1,'12121212',111)
    Data.update_path_filed(6,'1212')