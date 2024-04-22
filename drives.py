from DataBaseSession import DataBaseSession
from Computers import Computers
from server_Exceptions import SumOfDrivesIncompitable, DeviceAlreadyExsits
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
    INSERTION_QUERY = "INSERT INTO drives (mac,drive_type,drive_name,left_space) VALUES (%s,%s,%s,%s)"
    GET_DRIVE_BY_ID = "SELECT * FROM drives WHERE drive_id=%s"
    GET_DRIVES_BY_MAC = 'SELECT * FROM drives WHERE mac=%s'
    GET_ALL_DRIVES = 'SELECT * FROM drives'
    GET_MAX_LEFT_SIZE_ID = "select drive_id from drives order by left_space DESC "
    GET_MAX_LEFT_SIZE_IDS_ORDERD = "select drive_id, mac from drives order by left_space DESC"

    def _check_size(self,mac,drive_size):
        pc = Computers.GetComputer(mac)
        if drive_size > pc.size:
            return False
        drives = Drives.get_all_drives_by_mac(mac)
        if sum([drive[4] for drive in drives]) + drive_size > pc.size:
            return False
        return True
        
    def __init__(self, mac: str, drive_type:Union[bytes,int, DriveTypes], drive_name: str,space_granted:int) -> None:
        super().__init__() # might be to many connections 
        if isinstance(drive_type,bytes):
            drive_type = drive_type.decode()
        if isinstance(drive_type, str):
            drive_type = DriveTypes(drive_type)
        if isinstance(space_granted,bytes):
            space_granted = int(space_granted.decode())
        if not self._check_size(mac,space_granted):
            raise SumOfDrivesIncompitable()
        try:
            self.insert(Drives.INSERTION_QUERY,(mac,int(drive_type.value),drive_name,space_granted))    
        except IntegrityError:
            raise DeviceAlreadyExsits()
        self.mac = mac
        self.drive_type = drive_type
        self.drive_name = drive_name
        self.space_left = space_granted


    @staticmethod
    def get_drive_by_id(id: int):
        db = DataBaseSession()
        drive = db.fetch((Drives.GET_DRIVE_BY_ID,(id,)))
        del db
        return drive
    
        
    @staticmethod
    def get_all_drives_by_mac(mac):
        db = DataBaseSession()
        drives = db.fetch((Drives.GET_DRIVES_BY_MAC,(mac,)), all= True)
        del db
        return  drives
    
    @staticmethod
    def get_all_drives():
        db = DataBaseSession()
        drives = db.fetch(Drives.GET_ALL_DRIVES, all= True)
        del db
        return  drives
    
    @staticmethod
    def get_lowest_drive_mac():
        db = DataBaseSession()
        ans = db.fetch(get_lowet_drive_query, all=True)
        del db # just for clearence
        modefied_ans = [mac[0] for mac in ans]
        return modefied_ans
    
    @staticmethod
    def get_max_left_drive():
        db = DataBaseSession()
        ans = db.fetch(Drives.GET_MAX_LEFT_SIZE_ID, all=True)
        del db # just for clearence
        # modefied_ans = [mac[0] for mac in ans]
        return ans
        # returns the drive id for the drive with the maximum left space `  `
    @staticmethod
    def get_max_left_drive_and_mac():
        db = DataBaseSession()
        ans = db.fetch(Drives.GET_MAX_LEFT_SIZE_IDS_ORDERD, all=True)
        del db # just for clearence
        return ans
        # returns the dr
    def get_drive_used_size(drive_id:int):
        raise NotImplementedError()

if __name__ == "__main__":
    # drive = Drives('0xccd9ac32d1f7',1,'test22',10000)
    lst = Drives.get_drive_by_id(104)
    print('list: ',lst)
    # print(set(lst))
    # print(Drives.get_max_left_drive())
        
        