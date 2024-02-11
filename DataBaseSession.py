import mysql.connector as mc
from typing import Union

# class Computers:
DATABASE_IP = "10.100.102.204"
USERNAME = 'ariel'
PASSWORD = '112358'


class DataBaseSession:
    def __init__(self) -> None:
        
        self.db = mc.connect(host = DATABASE_IP, user = USERNAME, password = PASSWORD)
        self.cursor = self.db.cursor()
        self.insert('USE RAID;')
        
             

    def insert(self,query:str, values: Union[tuple,list]= None) -> None:
        if isinstance(values,list):
            self.cursor.executemany(query, values)
        elif values is None:
            self.cursor.execute(query)
        else: 
            self.cursor.execute(query,values)
        self.db.commit()
    
    def fetch(self,query: Union[tuple, str],all= True) -> iter:
        if isinstance(query, tuple):
            self.cursor.execute(query[0],query[1] )
        else:
            self.cursor.execute(query)
        return self.cursor.fetchall() if all else self.cursor.fetchone()
