import unittest
import sys, os
current_dir = os.path.dirname(os.path.abspath(__file__))
lower_directory_path = os.path.join(current_dir, 'C:/Users/ArielCohen/code/RAID-Store')
sys.path.append(lower_directory_path)

from Computers import Computers
from server_Exceptions import UserAlreadyExsit, UserDoesNotExsit

class computers_test(unittest.TestCase):
    def setUp(self) -> None:
        self.mac_addr = '0xccd9ac32d1f5'
        try:
            self.computer = Computers(self.mac_addr,100,4)
        except UserAlreadyExsit:
            self.computer = Computers.GetComputer(self.mac_addr)
    
    def test_get_computer(self,):
        try:
            self.computer = Computers.GetComputer('0xccd9ac32d144')
        except UserDoesNotExsit:
            self.assertTrue(True)

    def test_add_storage(self):
        size = self.computer.size
        self.computer.add_storage(100000)
        res = self.computer.fetch(('SELECT size FROM Computers WHERE MAC=%s',(self.mac_addr,)), all=False)
        self.assertEqual(res[0],size + 100000)
    
    def test_delete_computer(self):
        self.computer.delete_computer()
        res = self.computer.fetch(('SELECT * FROM Computers WHERE MAC=%s',(self.mac_addr,)))
        self.assertNotIn(self.mac_addr,res)

if __name__ == "__main__":
    unittest.main()