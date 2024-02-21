from DataBaseSession import DataBaseSession
class Data(DataBaseSession):
    GET_FIELD_QUERY = 'FROM Data SELECT * WHERE id=%s;'
    INSERT_FILED = 'INSERT INTO Data VALUES %s,%s,%s,%s,%s,%s,%s,%s,%s;'
    def __init__(self,id_num:int):
        super().__init__()
        data_field = self.fetch((Data.GET_FIELD_QUERY,(id_num)))
        self.hash_value = data_field[0]
        self.id_num = id
        self.size = data_field[2]
        self.path = data_field[3]
        self.relation = data_field[4]
        self.location = data_field[5]
        self.parity = data_field[6]
        self.segment = data_field[7]
        self.file_name = data_field[8]
    
    def CreateField(self,
        hash: str,
        id_num: int,
        size: int,
        path: str,
        relation: str,
        location: str,
        parity: bool,
        segment: int,
        file_name: str
    )->Data:
    insertion_fileds = (
        hash, id_num,size,path,relation,location,parityl,segment,file_name)
    self.insert(Data.INSERT_FILED,insertion_fileds)
    return Data(id_num)
    