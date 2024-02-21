import os,sys
from time import sleep
from random import randint
current_dir = os.path.dirname(os.path.abspath(__file__))
lower_directory_path = os.path.join(current_dir, 'E:/YUDB/project/RAID-Store')
sys.path.append(lower_directory_path)
from Query import Query
from SharedMemory import SharedMemory
from Semaphore import Semaphore
DEFAULT_SIZE = 64000
print('PID: '+str(os.getpid()))
sem = Semaphore('sema')
sh = SharedMemory('Ariel.tx',DEFAULT_SIZE)
for i in range(4):
    print('i: ', i)
    sem.acquire()
    try:
        req = Query.analyze_request(sh)
    except ValueError:
        i+=1
        continue
    print(req)
    sleep(randint(1,3))
    sem.release()
