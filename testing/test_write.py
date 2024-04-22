import os,sys
from time import sleep
from random import randint
current_dir = os.path.dirname(os.path.abspath(__file__))
lower_directory_path = os.path.join(current_dir, 'E:/YUDB/project/RAID-Store')
sys.path.append(lower_directory_path)
from Query import Query
from enums import Requests
from Semaphore import Semaphore
req_type = Requests.Add_File
MEMORY_NAME = 'Ariel.tx'
data = b'Hello\n'
sem = Semaphore('sema',1,1)
print('PID: '+str(os.getpid()))
re = Query(req_type,MEMORY_NAME,data = data)
for i in range(5):
    print('i: ', i)
    sem.acquire()
    re.build_req()
    sem.release()
    sleep(randint(1,3))
    re.data+=str(i).encode()
