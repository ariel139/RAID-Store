import unittest
import os,sys
current_dir = os.path.dirname(os.path.abspath(__file__))
lower_directory_path = os.path.join(current_dir, 'E:/YUDB/project/RAID-Store')
sys.path.append(lower_directory_path)
from Query import Query
from enums import Requests
from SharedMemory import SharedMemory

class TestRequest(unittest.TestCase):
    def setUp(self) -> None:
        self.mem_view = SharedMemory('test',2000)
        self.req = Query(Requests.Add_File,'Ariel.txt',self.mem_view, data=b'Hello dff')
    def test_init_data(self,):
        req_type = Requests.Add_File
        file_name = 'Ariel.tx'
        data = b'Hello qorld'
        re = Query(req_type,file_name,self.mem_view, data = data)
        self.assertEqual(re.file_name,file_name)
        self.assertEqual(re.method,req_type)
        self.assertEqual(re.data,data)
    
    def test_build_req(self,):
        print(self.req.build_req())
    
    def test_analyze_req(self,):
        data = b'\x00\x16*1*Ariel.txt*Hello dff'
        req_obj = self.req.analyze_request()
        # self.assertEqual(self.req.file_name,req_obj.file_name)
        # self.assertEqual(self.req.data,req_obj.data)
        # self.assertEqual(self.req.method,req_obj.method)
    
    def test__get_request_stream(self,):
        m_1= b'\x00'*1200
        m_2 = b'\x00'*1000
        res = self.req._get_request_stream()
        self.assertEqual(res,b'\x00'*1000)

    


if __name__ == "__main__":
    unittest.main()
