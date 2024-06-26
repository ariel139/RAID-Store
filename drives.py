"""
This class represents drives in the system.

Attributes:
    INSERTION_QUERY (str): SQL query template for inserting drive information into the drives table.
    GET_DRIVE_BY_ID (str): SQL query template for retrieving a drive by its ID.
    GET_DRIVES_BY_MAC (str): SQL query template for retrieving all drives by MAC address.
    GET_ALL_DRIVES (str): SQL query template for retrieving all drives.
    GET_MAX_LEFT_SIZE_ID (str): SQL query template for retrieving the drive with the maximum left space.
    GET_MAX_LEFT_SIZE_IDS_ORDERD (str): SQL query template for retrieving drive IDs ordered by maximum left space.
    GET_DRIVE_BY_MAC_AND_NAME (str): SQL query template for retrieving a drive by MAC address and name.

Methods:
    _check_size: Method to check if the granted space is compatible with available space.
    __init__: Constructor method to initialize a Drives object.
    get_drive_by_id: Static method to retrieve a drive by its ID.
    get_drive_by_mac_and_name: Static method to retrieve a drive by MAC address and name.
    get_all_drives_by_mac: Static method to retrieve all drives by MAC address.
    get_all_drives: Static method to retrieve all drives.
    get_lowest_drive_mac: Static method to retrieve the MAC address of the drive with the lowest space.
    get_max_left_drive: Static method to retrieve the drive with the maximum left space.
    get_max_left_drive_and_mac: Static method to retrieve the drive ID and MAC address with the maximum left space.
    get_drive_used_size: Static method to retrieve the used size of a drive (Not Implemented).

"""

from DataBaseSession import DataBaseSession
from Computers import Computers
from server_Exceptions import SumOfDrivesIncompitable, DeviceAlreadyExsits, NotenoughSpaceInTheDrive
from typing import Union
from enums import DriveTypes
from mysql.connector.errors import IntegrityError

get_lowet_drive_query = """
select drives.MAC 'MAC', SUM(drives.left_space) 'SUM_sizes'
from drives
GROUP BY drives.MAC
ORDER BY SUM_sizes DESC
"""

class Drives(DataBaseSession):
    INSERTION_QUERY = "INSERT INTO drives (mac, drive_type, drive_name, left_space) VALUES (%s, %s, %s, %s)"
    GET_DRIVE_BY_ID = "SELECT * FROM drives WHERE drive_id = %s"
    GET_DRIVES_BY_MAC = 'SELECT * FROM drives WHERE mac = %s'
    GET_ALL_DRIVES = 'SELECT * FROM drives'
    GET_MAX_LEFT_SIZE_ID = "SELECT * FROM drives ORDER BY left_space DESC"
    GET_MAX_LEFT_SIZE_IDS_ORDERD = """SELECT drives.drive_id, drives.mac
                                    FROM drives 
                                    JOIN data ON drives.drive_id = data.location 
                                    GROUP BY location 
                                    ORDER BY SUM(data.size) DESC"""
    GET_DRIVE_BY_MAC_AND_NAME = 'SELECT drive_id FROM drives WHERE mac = %s AND drive_name = %s'
    GET_DRIVE_USED_AMOUNT = 'SELECT SUM(size) from data WHERE location=%s'
    GET_LEFT_SPACE = 'SELECT left_space from drives WHERE drive_id = %s;'
    DECREASE_LEFT_SPACE = 'UPDATE drives SET left_space = left_space - %s WHERE drive_id = %s;'
    INCRESE_LEFT_SPACE = 'UPDATE drives SET left_space = left_space + %s WHERE drive_id = %s;'
    
    def _check_size(self, mac, drive_size):
        """
        Method to check if the granted space is compatible with available space.

        Args:
            mac (str): MAC address of the computer.
            drive_size (int): The size of the drive.

        Returns:
            bool: True if space is compatible, False otherwise.
        """
        pc = Computers.GetComputer(mac)
        if drive_size > pc.size:
            return False
        drives = Drives.get_all_drives_by_mac(mac)
        if sum([drive[4] for drive in drives]) + drive_size > pc.size:
            return False
        return True
    
    def __init__(self, mac: str, drive_type: Union[bytes, int, DriveTypes], drive_name: str, space_granted: int) -> None:
        """
        Constructor method to initialize a Drives object.

        Args:
            mac (str): MAC address of the drive.
            drive_type (Union[bytes, int, DriveTypes]): The type of the drive.
            drive_name (str): The name of the drive.
            space_granted (int): The granted space of the drive.

        Raises:
            SumOfDrivesIncompitable: If the sum of drives is incompatible with available space.
            DeviceAlreadyExsits: If the drive already exists.

        Attributes:
            mac (str): MAC address of the drive.
            drive_type (Union[bytes, int, DriveTypes]): The type of the drive.
            drive_name (str): The name of the drive.
            space_left (int): The left space of the drive.
        """
        super().__init__() 
        if isinstance(drive_type, bytes):
            drive_type = drive_type.decode()
        if isinstance(drive_type, str):
            drive_type = DriveTypes(drive_type)
        if isinstance(space_granted, bytes):
            space_granted = int(space_granted.decode())
        if not self._check_size(mac, space_granted):
            raise SumOfDrivesIncompitable()
        try:
            self.insert(Drives.INSERTION_QUERY, (mac, int(drive_type.value), drive_name, space_granted))    
        except IntegrityError:
            raise DeviceAlreadyExsits()
        self.mac = mac
        self.drive_type = drive_type
        self.drive_name = drive_name
        self.space_left = space_granted

    @staticmethod
    def get_drive_by_id(id: int):
        """
        Static method to retrieve a drive by its ID.

        Args:
            id (int): The ID of the drive.

        Returns:
            tuple: A tuple representing the drive.
        """
        db = DataBaseSession()
        drive = db.fetch((Drives.GET_DRIVE_BY_ID, (id,)))
        del db
        return drive
    
    @staticmethod
    def get_drive_by_mac_and_name(mac: str, name: str):
        """
        Static method to retrieve a drive by MAC address and name.

        Args:
            mac (str): The MAC address of the drive.
            name (str): The name of the drive.

        Returns:
            int: The ID of the drive, or None if not found.
        """
        db = DataBaseSession()
        drive_id = db.fetch((Drives.GET_DRIVE_BY_MAC_AND_NAME, (mac, name)))
        del db
        return drive_id[0] if drive_id is not None else drive_id
    
    @staticmethod
    def get_all_drives_by_mac(mac):
        """
        Static method to retrieve all drives by MAC address.

        Args:
            mac (str): The MAC address of the computer.

        Returns:
            list: A list of tuples representing drives.
        """
        db = DataBaseSession()
        drives = db.fetch((Drives.GET_DRIVES_BY_MAC, (mac,)), all=True)
        del db
        return drives
    
    @staticmethod
    def get_all_drives():
        """
        Static method to retrieve all drives.

        Returns:
            list: A list of tuples representing drives.
        """
        db = DataBaseSession()
        drives = db.fetch(Drives.GET_ALL_DRIVES, all=True)
        del db
        return drives
    
    @staticmethod
    def get_lowest_drive_mac():
        """
        Static method to retrieve the MAC address of the drive with the lowest space.

        Returns:
            list: A list of MAC addresses.
        """
        db = DataBaseSession()
        ans = db.fetch(get_lowet_drive_query, all=True)
        del db
        modefied_ans = [mac[0] for mac in ans]
        return modefied_ans
    
    @staticmethod
    def get_max_left_drive():
        """
        Static method to retrieve the drive with the maximum left space.

        Returns:
            list: A list of tuples representing drives.
        """
        db = DataBaseSession()
        ans = db.fetch(Drives.GET_MAX_LEFT_SIZE_ID, all=True)
        del db
        return ans
    
    @staticmethod
    def get_max_left_drive_and_mac():
        """
        Static method to retrieve the drive ID and MAC address with the maximum left space.

        Returns:
            list: A list of tuples representing drive ID and MAC address.
        """
        db = DataBaseSession()
        ans = db.fetch(Drives.GET_MAX_LEFT_SIZE_ID, all=True)
        del db
        return ans
    
    @staticmethod
    def get_drive_used_size(drive_id: int):
        """
        Static method to retrieve the used size of a drive.

        Args:
            drive_id (int): The ID of the drive.

        Raises:
            NotImplementedError: Method not implemented.

        Returns:
            None: Not implemented.
        """
        db = DataBaseSession()
        ans = db.fetch((Drives.GET_DRIVE_USED_AMOUNT,(drive_id,)))[0]
        return 0 if ans is None else int(ans)

    @staticmethod
    def decrease_left_size(drive_id: int, amount:int):
        db = DataBaseSession()
        ans = db.fetch((Drives.GET_LEFT_SPACE, (drive_id,)))
        if ans is None: raise ValueError('Invalid drive id')
        if ans[0]<amount:
            raise NotenoughSpaceInTheDrive('There is not enough space for the amount garnted')
        db.insert(Drives.DECREASE_LEFT_SPACE,(amount,drive_id))
    
    @staticmethod
    def increase_left_size(drive_id: int, amount:int):
        db = DataBaseSession()
        db.insert(Drives.INCRESE_LEFT_SPACE,(amount,drive_id))
    
   
if __name__ == "__main__":
    # drive = Drives('0xccd9ac32d1f7',1,'test22',10000)
    lst = Drives.get_connected_drives_to_real(120)
    print('list: ', lst)
