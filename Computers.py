from DataBaseSession import DataBaseSession
from typing import Union
from enums import Countries
class Computers(DataBaseSession):
    NEW_ROW = "NSERT INTO Computers VALUES (%s, %s, %s ,%s , %s)"
    GET_ROW = "SELECT * FROM Computers WHERE mac = %s"
    def __init__(self,mac: str, ip: str, size:int, location: Union[Countries,int]) -> None:
        super().__init__()
        if isinstance(location, Countries):
            self.location = location.value
        else: 
            self.location = location
        self.insert(Computers.NEW_ROW,(mac, ip, size, self.location))
        self.mac = mac
        self.ip = ip
        self.size = size
    
    @classmethod
    def GetComputer(cls, mac: str):
        super().__init__()
        query = Computers.GET_ROW, (mac,)
        row = cls.fetch(query,all=False)
        return cls(row[0], row[1], row[2],row[3])

mac = '11111'
ip = '11111'
size = 1222
country = Countries.Israel
pc = Computers(mac,ip,size,country)
        