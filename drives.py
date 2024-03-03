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
    def _check_size(self,mac,drive_size):
        pc = Computers.GetComputer(mac)
        if drive_size > pc.size:
            return False
        drives = Drives.get_all_drives_by_mac(mac)
        if sum([drive[4] for drive in drives]) + drive_size > pc.size:
            return False
        return True
        
    def __init__(self, mac: str, drive_type:Union[bytes,int, DriveTypes], drive_name: str,space_granted:int) -> None:
        super().__init__()
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
        self.space_granted = space_granted

    def get_drive_by_id(self,id: int):
        drive = self.fetch((Drives.GET_DRIVE_BY_ID,(id,)))
        return Drives(drive[0],drive[2],drive[3],drive[4])
    
    def get_all_drives_by_mac(mac):
        db = DataBaseSession()
        drives = db.fetch((Drives.GET_DRIVES_BY_MAC,(mac,)), all= True)
        return drives
    
    @staticmethod
    def get_lowest_drive_mac():
        db = DataBaseSession()
        ans = db.fetch(get_lowet_drive_query, all=True)
        del db # just for clearence
        modefied_ans = [mac[0] for mac in ans]
        return modefied_ans

# drive = Drives('0xccd9ac32d1f7',1,'test22',10000)
# # drive.get_drive_by_id(4)
# lst = Drives.get_lowest_drive_mac()
# print('list: ',lst)
# print(set(lst))
        
        
        