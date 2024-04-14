from pathlib import Path
from platform import system
import os.path as pathpk
from os import mkdir
class MountingMangager:
    def __init__(self,mount_point:str, partition_path:str, size:int) -> None:
        self._cheak_type(mount_point,str)
        self._cheak_type(partition_path,str)
        self._cheak_type(size,int)

        self.mount_point = Path(mount_point)
        self.partition_path = Path(partition_path)
        self.size = size
        self.os_type = system()
        pass

    def mount_partition(self,):
        self._create_mount_point()
        if self.os_type == 'Linux':
            pass
        elif self.os_type == 'Windows':
            pass
    
    def _create_mount_point(self,):
        if not pathpk.exists(self.mount_point):
            mkdir(self.mount_point)

    def _cheak_type(self,var:object, expected_type:type):
        if not isinstance(var,expected_type):
            raise TypeError(f'{var} is not the expected type: got {type(var)} expected {expected_type}')
    
