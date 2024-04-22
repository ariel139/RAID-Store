from time import sleep
import math
import traceback
import socket
from typing import  Tuple
from threading import Thread, Lock
from Message import Message
from node import Node
from enums import Countries,Category, Requests
from Computers import Computers
from queue import Queue
from Semaphore import Semaphore
from server_Exceptions import *
from Query_Request import Query_Request, DEFAULT_SIZE
from SharedMemory import SharedMemory
from drives import Drives
from RAID import give_drivers, xor_buffers
from pickle import dumps, loads
from gc import get_objects
from hashlib import sha256
from Data import Data
from AES_manager import AESCipher
from User import User
from struct import unpack

CHUNK_SIZE = 1_000_000
MAX_SUB_THREADS = 5

SERVER_SHARED_MEMORY_NAME ='server_shared_memory'
SERVER_SEMAPHORE_NAME = 'server_sem_signal'
GUI_SHARED_MEMORY_NAME ='gui_shared_memory'
GUI_SEMAPHORE_NAME = 'gui_sem_signal'

# global vars
running = True
sessions = {} # key: node_key value: mac
nodes = [] # list of nodes connected
messages_queues = {} # key: node_hash value:queue
messages_queue_locker = Lock()
session_locker = Lock()
nodes_locker = Lock()
def lock(locker: Lock):
    def lock_deco(func):
        def wrapper(*args, **kwargs):
            locker.acquire()
            func(*args, **kwargs)
            locker.release()
        return wrapper
    return lock_deco

@ lock(session_locker)
def add_seesion(node_key:str, mac:str):
    global sessions
    sessions[node_key] = mac

@lock(messages_queue_locker)
def add_queue(node_key:int, queue:Queue):
    global messages_queues
    messages_queues[str(node_key)] = queue

@lock(messages_queue_locker)
def remove_queue(node_key:int):
    global messages_queues
    del messages_queues[str(node_key)]



def find_node_by_mac(mac:str)-> Node:
    node = ''
    for node_key in sessions:
        if sessions[node_key] == mac:
            node = node_key
    session_locker.release()
    nodes_locker.acquire()
    for node_v in nodes: 
        if node == hash(node_v):
            node = node_v
    nodes_locker.release()
    return node


def xor_drives(drives_buffers: dict):
    for _,buffer in drives_buffers.items():
        if len(buffer) <=0:
            return
    slicer_index = min([len(value) for key, value in drives_buffers.items()])
    to_xor = [buf[:slicer_index] for key, buf in drives_buffers.items()]
    for i in drives_buffers.keys():
        drives_buffers[i] = drives_buffers[i][slicer_index:]
    return xor_buffers(tuple(to_xor))

def xor_data(q: Queue, res_drive: tuple, drives_amount, name)->bytes:
    drives_buffers = {}
    parity_node = find_node_by_mac(res_drive[0])
    dones = set()
    while True:
        if not q.empty():
            mac, drive_info, done, data = q.get()
            drive_idef = sha256(mac.encode()+drive_info.encode()).hexdigest()
            if done:
                dones.add(drive_idef)
            if drive_idef in drives_buffers.keys():
                drives_buffers[drive_idef]+=data
            else: 
                drives_buffers[drive_idef] = data
        if len(drives_buffers) >= drives_amount:
            xord_data_buffer = xor_drives(drives_buffers)
            if xord_data_buffer is not None:
                #TODO: add parity record to Data table
                name.to_bytes(math.ceil(math.log2(len(str(name)))),'little')
                msg = Message(Category.Recovering,10,(res_drive[3],name, xord_data_buffer))
                parity_node.send(msg)
        if len(dones) == len(drives_buffers.keys()) and len(dones)>0:
            real_done = True
            for key, data in drives_buffers.items():
                if len(data) > 0:
                    real_done = False
            if real_done:
                break


def create_parity(drives:list):
    # d_1 + d_2 are getting xor'd
    #d_3 get the result
    if len(drives) <3:
        raise NotEnoghDrivesConnected()
    parity_drive = max(drives, key= lambda drive: drive[4])
    #BUG: left space is thinked as how much is occupied by the drive 
    nodes_drives = []
    for drive in drives:
        if drive == parity_drive:
            continue
        nodes_drives.append((find_node_by_mac(drive[0]),drive))
    reciving_q = Queue()
    pickeld_q_id = dumps(id(reciving_q))
        # messages_q.put((message, 0)) # might need a lock
    for node,drive in nodes_drives:
        node_msg_q = messages_queues[str(hash(node))]
        msg = Message(Category.Recovering,7,(pickeld_q_id,drive[3])) # in client side get by name and mac from db
        node_msg_q.put((msg, 0))
    xor_data(reciving_q, parity_drive, len(nodes_drives), str(hash(str(nodes_drives))))
    # .# node_2.send(msg_req_2)
    

def add_storage(data):
    drive_to_put = Drives.get_max_left_drive()
    session_locker.acquire()
    all_macs = [sessions[key] for key in sessions]
    session_locker.release()
    node = find_node_by_mac(drive_to_put[0])    
    node.send(data)
    if len(all_macs) >=3:
        all_drives = [drive if drive[0] in all_macs else None for drive in Drives.get_all_drives()]
        if len(all_drives) > 3:
            drives = give_drivers(drive_to_put,all_drives)
            create_parity(drives)

def get_object_from_rb(obj_id:int):
    t_obj = None
    for obj in get_objects():
        if id(obj) == obj_id:
            t_obj = obj
            break
    if t_obj is None: ObjectNotFoundInRecycleBean()
    return t_obj
def handle_chuncked_data(msg: Message):
    q_id = loads(msg.data[0])
    mac = msg.data[1].decode()
    drive_name  = msg.data[2].decode()
    q = None
    for obj in get_objects():
        if id(obj) == q_id:
            q = obj
            break
    if q is None: raise ObjectNotFoundInRecycleBean('Could not find q object')
    q.put((drive_name,mac, unpack('?',msg.data[3])[0], msg.data[4]))
    return None


def handle_request(message: Message, node_key:int):
    global sessions
    category = Category(message.category)
    match (category):
        case Category.Authentication:
            if message.opcode == 1:
                 # endpoint sign up
                mac = message.data[0].decode()
                try:
                    pc = Computers(mac,message.data[1].decode(), message.data[2].decode())
                except UserAlreadyExsit:
                    return Message(Category.Errors,2)
                add_seesion(str(node_key),mac)
                return Message(Category.Authentication,5)
            elif message.opcode == 2:
                # delete endpoint 
                mac = sessions[str(node_key)]
                pc = Computers.GetComputer(mac)
                #TODO: handle moving the data to other source of storage
                pc.delete_computer()
                return Message(Category.Authentication, 6)
            elif message.opcode == 3:
                #endpoint signin
                mac = message.data[0].decode()
                try:
                    pc = Computers.GetComputer(mac)
                    add_seesion(str(node_key),mac)
                except UserDoesNotExsit:
                    return Message(Category.Errors,1)
                return Message(Category.Authentication,5)
            else:
                return Message(Category.Errors,3)
                # error
        case Category.Status:
            if message.opcode == 2:
                #TODO: handle moving the data temporerly
                return Message(Category.Status,3)
            pass
        case Category.Storage:
            # add storage space
            if message.opcode == 0:
                mac = sessions[str(node_key)]
                pc = Computers.GetComputer(mac)
                try:
                    pc.add_storage(message.data[0])
                except SizeToLow:
                    return Message(Category.Errors,5,'The Size of the messgae is To Low')
                return Message(Category.Storage,6)
            elif message.opcode == 2:
                Data.update_path_filed(int(message.data[1].decode()),message.data[0].decode())
                print('got file ACK ')
            elif message.opcode == 5:
                #TODO: check if file found error
                buffer_id = loads(message.data[2])
                file_obj = get_object_from_rb(buffer_id)
                file_obj[0] =message.data[0]
                file_obj[1] = message.data[1].decode()
            elif message.opcode == 7:
                mac = sessions[str(node_key)]
                try:
                    Drives(mac,message.data[0],message.data[1],message.data[2])
                    return Message(Category.Storage,8)
                except SumOfDrivesIncompitable:
                    return Message(Category.Errors,5,('The size of the drive is to high from the space you granted, add more space before',))
                except DeviceAlreadyExsits:
                    return Message(Category.Errors,6,)   
        case Category.Recovering:
            if message.opcode == 8:
                return handle_chuncked_data(message)
        case Category.Errors:
            if message.opcode == 4:
                print(message.data[0].decode())
            pass
        case _:
            return Message(Category.Errors,3)
            #error in messgae format


def handle_requests(message: Message, q: Queue, key:int, id: str):
    try:
        res = handle_request(message, key)
    except Exception as error:
        traceback.print_exc()
        res = Message(Category.Errors,0)
    q.put((res,id))

def send_messages(node: Node, q: Queue):
    while True:
        val = q.get()
        if val == 'stop':
            break
        message, id  = val
        if isinstance(message, Message):
            node.send(message,id)
        else:
            print(f'did not send message {str(message)}')

def request_to_message(req:Query_Request, *args)-> Message:
    match (req.method):
        case Requests.Add_File:
            file_data = req.data
            file_name = req.file_name
            file_hash = sha256(file_data).hexdigest()
            if isinstance(args[0], str):
                desierd_drive = args[0].encode()
            if not args[1]:
                raise ValueError('missing data files id')
            #TODO: add reed-solomon 
            return Message(Category.Storage,1,(file_data,file_hash,file_name, desierd_drive,args[1].encode()))
            # add file
            pass 
        case Requests.Delete_File:
            # make sure to retrive file path and other importent parameters
            return Message(Category.Storage,3,)
            # delete file
        case Requests.Retrive_File:
            # retrive file for client
            pass
        case _:
            # error
            pass

def get_gui_requests(gui_sem:Semaphore,server_sem:Semaphore,gui_shr:SharedMemory,server_shr: SharedMemory):
    global running
    while running:
        try:
            gui_sem.acquire()
            try:
                req = Query_Request.analyze_request(gui_shr)
                # message = request_to_message(req)
                reciver = handle_request_q(req)
            except Exception as err:
                res_data = ('General error', err)
                response = Query_Request(Requests.Error,data=dumps(res_data), memory_view=server_shr)
            else:
                res_data = ('Success',reciver)
                response = Query_Request(Requests.Response,data=dumps(res_data), memory_view=server_shr)
            finally:
                response.build_req()
                server_sem.release()
        except Exception as err:
            traceback.print_exc()
        # messages_q = messages_queues[hash(reciver)]
        # messages_q.put((message, 0)) # might need a lock

def get_right_drive(connected_macs:list, drives_macs: list):
    drive_id = None
    drives_mac = None
    for id, mac in drives_macs:
        if mac in connected_macs:
            drive_id = id
            drives_mac = mac
            break
    return drive_id, drives_mac
def get_file_info(file_id:int):
    if isinstance(file_id,str):
        if file_id.isnumeric():
            file_id = int(file_id)
    elif isinstance(file_id,int):
        pass
    else:
        raise InvalidFileId() # invalid file_id exeption
    data_filed = Data(file_id)
    return data_filed
    
def get_file_from_node(node: Node, path:str)-> bytes:
    drive = path[:path.find('\\')]
    file_data = [b'1','1']
    msg = Message(Category.Storage,4,(path,drive, dumps(id(file_data)), dumps(id(file_data))))
    messages_q = messages_queues[str(hash(node))]
    messages_q.put((msg, 0))
    while len(file_data[0])==1 and len(file_data[1]) == 1:
        continue
    sleep(0.5) # in case it uplodes the buffer to soon before the hash 
    if len(file_data[1]) ==1 and len(file_data[0])>1:
        return False, file_data[1]
        # in case there is somethig in the hash and not in the buffer it means an error eccourd
    return True, file_data[0]

def handle_request_q(req:Query_Request):
    if req.method == Requests.Add_File:
        session_locker.acquire()
        all_macs = [sessions[key] for key in sessions]
        session_locker.release()
        macs_drives_lst = Drives.get_max_left_drive_and_mac()
        #TODO: change left size in the drive
        drive_id, drives_mac = get_right_drive(all_macs, macs_drives_lst)
        if drive_id is None and drives_mac is None:
            print('NoNodescurrentlyConnected()') #TODO: handle response to gui
            return
        node = find_node_by_mac(drives_mac)
        drive = Drives.get_drive_by_id(drive_id)
        user_id = bytearray(req.data[:req.data.find(b'*')])
        aes_key = User.get_AES_key_by_id(user_id.decode())
        aes_obj = AESCipher(aes_key)
        req.data = aes_obj.encrypt(req.data[req.data.find(b'*')+1:])
        d_id = str(Data.CreateFieldNoPath(user_id.decode(),drive_id,sha256(req.data).hexdigest(),len(req.data)).id_num)
        msg = request_to_message(req, drive[3], d_id)
        messages_q = messages_queues[str(hash(node))]
        messages_q.put((msg, 0)) # might need a lock
        # get from nodes the ids and then get the desierd drive to add
        if len(all_macs) >=3:
            all_drives = Drives.get_all_drives()
            filterd_drives = list(filter(lambda drive: drive[0] in all_macs, all_drives))
            drives = give_drivers(Drives.get_drive_by_id(drive_id),filterd_drives)
            create_parity(drives)
            return 'file uploded with parity drive'
        return 'file uploded with no parity drive'
    elif req.method == Requests.Files_List:
        records = Data.get_data_records()
        records = list(filter(lambda record: not None in record,records))
        return records
    elif req.method == Requests.Retrive_File:
        file_meta_data = get_file_info(req.file_name)
        file_mac = Drives.get_drive_by_id(file_meta_data.location)[0]
        file_node = find_node_by_mac(file_mac)
        if file_node is None:
            raise FileNodeNotCurrentlyConnected()
        worked, file_data = get_file_from_node(file_node, file_meta_data.path)
        if worked:
            aes_key = User.get_AES_key_by_id(file_meta_data.relation)
            aes_manage = AESCipher(aes_key)
            decrypted = aes_manage.decrypt(file_data)
            return decrypted
        else:
            raise UnableToUploadFile(file_data)
        
def find_node_by_mac(mac:str) -> Node:
    nodes_locker.acquire()
    node_keys = [(hash(node),node) for node in nodes]
    nodes_locker.release()
    for key in node_keys:
        if sessions[str(key[0])] == mac:
            return key[1]
    return None
def handle_client(client_soc: socket.socket):
    global nodes
    try:
        end_point = Node(client_soc)
        nodes_locker.acquire()
        nodes.append(end_point)
        nodes_locker.release()
        send_message_queue = Queue()
        add_queue(hash(end_point),send_message_queue)
        handle_requests_threads = []
        send_msg_thread = Thread(target=send_messages,args=(end_point,send_message_queue))
        send_msg_thread.start()
        handle_requests_threads.append(send_msg_thread)
        while running:
            while len(handle_requests_threads) <= MAX_SUB_THREADS:
                message,id  = end_point.recive()
                th = Thread(target=handle_requests, args = (message,send_message_queue,hash(end_point), id))
                th.start()
                handle_requests_threads.append(th)
    finally:
        send_message_queue.put('stop')
        remove_queue(hash(end_point))
        session_locker.acquire()
        del sessions[str(hash(end_point))]
        session_locker.release()
        nodes_locker.acquire()
        nodes.remove(end_point)
        nodes_locker.release()
        for th in handle_requests_threads:
            th.join()


def main(creds: Tuple[str, int ]):
    try:
        global running
        gui_sem = None
        server_sem = None
        server_socket = socket.socket()
        server_socket.bind(creds)
        server_socket.listen(5)
        print('SERVER running...')
        gui_sem = Semaphore(GUI_SEMAPHORE_NAME, initial_value=0)
        server_sem = Semaphore(SERVER_SEMAPHORE_NAME,initial_value=0)
        gui_shr = SharedMemory(GUI_SHARED_MEMORY_NAME,DEFAULT_SIZE)
        server_shr = SharedMemory(SERVER_SHARED_MEMORY_NAME,DEFAULT_SIZE)
        gui_thread = Thread(target=get_gui_requests,args=(gui_sem,server_sem,gui_shr,server_shr))
        gui_thread.start()
        while running:
            soc, addr = server_socket.accept()
            print('new connection from: '+addr[0]+':'+str(addr[1]))
            threads = []
            th = Thread(target=handle_client, args= (soc,))
            th.start()
            threads.append(th)
    except Exception as err:
        print('got error: ',err)
        traceback.print_exc()
    finally:
        if gui_sem is not None:
            del gui_sem
        gui_shr.close()
        server_socket.close()
        for th in threads:
            th.join()

            

            
if __name__ == "__main__":
    main(('10.100.102.204',8200))