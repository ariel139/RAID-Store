import unittest
import sys, os

current_dir = os.path.dirname(os.path.abspath(__file__))
lower_directory_path = os.path.join(current_dir, 'C:/Users/ArielCohen/code/RAID-Store')
sys.path.append(lower_directory_path)
from enums import Category
from Message import Message
class Message_Test(unittest.TestCase):
    def setUp(self) -> None:
        self.Message = Message(Category.Authentication,1,b'\x05\x00<Para\x08\x00<Paramet\x06\x00<Param')
    def test_init_byte(self,):
        self.Message  = Message(Category.Authentication,1,b'\x05\x00<Para\x08\x00<Paramet\x06\x00<Param')
        self.assertEqual(self.Message.category, 1)
        self.assertEqual(self.Message.opcode, 1)
        self.assertEqual(self.Message.data, (b'<Para',b'<Paramet',b'<Param'))
        self.assertEqual(self.Message.size, int(len(b'\x00\x05<Para\x00\x08<Paramet\x00\x06<Param')+3).to_bytes(2,'big'))
    
    def test_init_tuple(self,):
        self.Message  = Message(Category.Authentication,1,('hello','my','name','is','ariel'))
        self.assertEqual(self.Message.category, 1)
        self.assertEqual(self.Message.opcode, 1)
        self.assertEqual(self.Message.data, (b'hello',b'my',b'name',b'is',b'ariel'))
        self.assertEqual(self.Message.size, int(len(''.join(('hello','my','name','is','ariel')))+10+3).to_bytes(2,'big'))

    def test_build_message(self,):
        msg = b'\x00\x1c'+b'!'+b'\x00\x01'+b'\x05\x00<Para\x08\x00<Paramet\x06\x00<Param'
        self.assertEqual(self.Message.build_message(1),msg)
    
    def test_parse_response(self):
        x =  Message.parse_response( b'\x00\x1c'+b'!'+b'\x00\x01'+b'\x05\x00<Para\x08\x00<Paramet\x06\x00<Param')
        val = self.Message == self.Message
        self.assertTrue(val)
    
if __name__ == "__main__":
    unittest.main()
