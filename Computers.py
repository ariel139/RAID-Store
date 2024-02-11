from DataBaseSession import DataBaseSession
from typing import Union
from enums import Countries
import server_Exceptions
from mysql.connector import IntegrityError
from sys import exit
class Computers(DataBaseSession):
    NEW_ROW = "INSERT INTO Computers VALUES (%s, %s ,%s )"
    GET_ROW = "SELECT * FROM Computers WHERE mac = %s"
    DELETE_ROW = 'DELETE FROM Computers WHERE mac = %s'
    def __init__(self,mac: str, size:int, location: Union[Countries,int], exsit=False) -> None:
        super().__init__()
        if isinstance(location, Countries):
            self.location = location.value
        else: 
            self.location = location
        if not exsit:
            try:
                self.insert(Computers.NEW_ROW,(mac, size, self.location))
                self.mac = mac
                self.size = size
            except IntegrityError:
                raise server_Exceptions.UserAlreadyExsit
            except Exception as error:
                print(error)
        else:
            self.mac = mac
            self.size = size
            self.location = location
    
    @classmethod
    def GetComputer(cls, mac: str):
        db_session = DataBaseSession()
        query = Computers.GET_ROW, (mac,)
        row = db_session.fetch(query,all=False)
        if row is None:
            raise server_Exceptions.UserDoesNotExsit
        del db_session # just for de-allocating the heap
        return Computers(row[0], row[1], row[2], exsit= True)

    def delete_computer(self):
        query = Computers.DELETE_ROW
        self.insert(query,(self.mac,))
    
    def add_storage(self,size: Union[int, bytes]):
        if isinstance(size, bytes):
            size = int(size.decode())
        get_size_query = "SELECT size FROM Computers WHERE mac = %s"
        update_size_query = 'UPDATE Computers SET size = %s WHERE MAC=%s'
        real_size = self.fetch((get_size_query,(self.mac,)),all=False)[0]
        if int(real_size) + int(size) < 1 : 
            raise server_Exceptions.SizeToLow('The desird size is lower then 1')
        else:
            new_size = real_size +size
            self.insert(update_size_query,(new_size,self.mac))


