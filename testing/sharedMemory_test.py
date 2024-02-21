import unittest
import sys, os

current_dir = os.path.dirname(os.path.abspath(__file__))
lower_directory_path = os.path.join(current_dir, 'E:/YUDB/project/RAID-Store')
sys.path.append(lower_directory_path)
from SharedMemory import SharedMemory

class SharedMemory_Test(unittest.TestCase):
    def setUp(self) -> None:
        self.shr = SharedMemory('Ariel',10)

    def test_check_create_file(self,):
        shr = SharedMemory('Ariel',10)
        self.assertEqual(shr.size,10)
        self.assertEqual(shr.name,'Ariel')
    
    def test_check_no_file(self,):
        shr = SharedMemory('Ariel',10, False)
        self.assertEqual(shr.size,10)
        self.assertEqual(shr.name,'Ariel')
    
    def test_write(self):
        self.shr.write(b'Ariel')
        input()
    
    def test_read(self,):
        data = self.shr.read(5)
        self.assertEqual(b'Ariel',data)
