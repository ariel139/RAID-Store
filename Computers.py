"""
This class represents computer entities in the system.

Attributes:
    NEW_ROW (str): SQL query template for inserting a new row into the Computers table.
    GET_ROW (str): SQL query template for retrieving a row from the Computers table.
    DELETE_ROW (str): SQL query template for deleting a row from the Computers table.

Methods:
    __init__: Constructor method to initialize a Computers object.
    GetComputer: Class method to retrieve a computer object based on MAC address.
    delete_computer: Method to delete the computer from the database.
    add_storage: Method to add storage size to the computer.
"""

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
    GET_COUNT = 'SELECT COUNT(MAC) FROM computers'
    def __init__(self, mac: str, size: int, location: Union[Countries, int], exsit=False) -> None:
        """
        Constructor method to initialize a Computers object.

        Args:
            mac (str): The MAC address of the computer.
            size (int): The size of the computer.
            location (Union[Countries, int]): The location of the computer, either a country enum or an integer.
            exsit (bool): Flag indicating whether the computer already exists in the database (optional, default is False).
        
        Raises:
            UserAlreadyExsit: If a computer with the provided MAC address already exists in the database.
        """
        super().__init__()
        
        if isinstance(location, Countries):
            self.location = location.value
        else:
            self.location = location
        
        if not exsit:
            try:
                self.insert(Computers.NEW_ROW, (mac, size, self.location))
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
        """
        Class method to retrieve a computer object based on MAC address.

        Args:
            mac (str): The MAC address of the computer.

        Returns:
            Computers: A Computers object representing the computer.

        Raises:
            UserDoesNotExsit: If a computer with the provided MAC address does not exist in the database.
        """
        db_session = DataBaseSession()
        query = Computers.GET_ROW, (mac,)
        row = db_session.fetch(query, all=False)
        if row is None:
            raise server_Exceptions.UserDoesNotExsit
        del db_session # just for de-allocating the heap
        return Computers(row[0], row[1], row[2], exsit=True)

    def delete_computer(self):
        """
        Method to delete the computer from the database.
        """
        query = Computers.DELETE_ROW
        self.insert(query, (self.mac,))
    
    def add_storage(self, size: Union[int, bytes]):
        """
        Method to add storage size to the computer.

        Args:
            size (Union[int, bytes]): The size to be added, either an integer or bytes.

        Raises:
            SizeToLow: If the desired size is lower than 1.
        """
        if isinstance(size, bytes):
            size = int(size.decode())
        get_size_query = "SELECT size FROM Computers WHERE mac = %s"
        update_size_query = 'UPDATE Computers SET size = %s WHERE MAC=%s'
        real_size = self.fetch((get_size_query, (self.mac,)), all=False)[0]
        if int(real_size) + int(size) < 1: 
            raise server_Exceptions.SizeToLow('The desired size is lower than 1')
        else:
            new_size = real_size + size
            self.insert(update_size_query, (new_size, self.mac))
        
    @staticmethod
    def get_connected_count():
        db_session = DataBaseSession()
        ans = db_session.fetch(Computers.GET_COUNT)[0]
        return ans
    
