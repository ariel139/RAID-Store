from struct import pack, unpack
from time import sleep
from parties import Parties
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
from info_retrive import *
from pathlib import Path

CHUNK_SIZE = 1_000_000
MAX_SUB_THREADS = 30

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
    dones = set()
    if res_drive is not None:
        parity_node = find_node_by_mac(res_drive[0])
    else:
        res_drive_buffer = b''
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
                # name.to_bytes(math.ceil(math.log2(len(str(name)))),'little')
                if res_drive is None:
                    res_drive_buffer+=xord_data_buffer
                else:
                    msg = Message(Category.Recovering,10,(res_drive[3],name, xord_data_buffer))
                    parity_node.send(msg)
        if len(dones) == len(drives_buffers.keys()) and len(dones)>0:
            cnt = 0
            for key, data in drives_buffers.items():
                if len(data) > 0:
                    cnt+=1
            if cnt==0:
                break
            if cnt ==1:
                for key, data in drives_buffers.items():
                    if len(data) == 0:
                        drives_buffers[key] = b'\x00'*max([len(data) for key,data in drives_buffers.items()])
    print('finished xoring')
    if res_drive is None:
        return res_drive_buffer

def remove_used_drive_in_data_from_list(drives:list):
    drives_cp = drives.copy()
    drives_ids = Data.get_all_drives_ids()
    for drive in drives_cp:
        if drive[1] in drives_ids:
            drives_cp.remove(drive)
    return drives_cp

def send_parity_request_to_drive(drive:tuple, pickeld_q_id):
    zero_index = pack('L',socket.htonl(0))
    drive_node = find_node_by_mac(drive[0])
    node_msg_q = messages_queues[str(hash(drive_node))] 
    msg = Message(Category.Recovering,7,(pickeld_q_id,drive[3],zero_index)) # in client side get by name and mac from db
    node_msg_q.put((msg, 0))

def create_parity(used_drive, second_drive, parity_drive):
    # d_1 + d_2 are getting xor'd
    #d_3 get the result
    #BUG: left space isno_used_drives_lst thinked as how much is occupied by the drive 
    reciving_q = Queue()
    pickeld_q_id = dumps(id(reciving_q))
        # messages_q.put((message, 0)) # might need a lock
    send_parity_request_to_drive(used_drive,pickeld_q_id)
    send_parity_request_to_drive(second_drive,pickeld_q_id)

    # for node,drive in nodes_drives:
    #     node_msg_q = messages_queues[str(hash(node))] 
    #     msg = Message(Category.Recovering,7,(pickeld_q_id,drive[3],zero_index)) # in client side get by name and mac from db
    #     node_msg_q.put((msg, 0))
    parity_file_name = sha256(str(parity_drive[:3]).encode()).hexdigest()
    xor_data(reciving_q, parity_drive, 2, parity_file_name)
    if not Parties.is_connected_to_parity(used_drive[1]):
        Parties.connect_drives_to_parity([used_drive[1],second_drive[1]],parity_drive[1])
    print('finished all')
    # .# node_2.send(msg_req_2)
    

# def add_storage(data):
#     drive_to_put = Drives.get_max_left_drive()
#     session_locker.acquire()
#     all_macs = [sessions[key] for key in sessions]
#     session_locker.release()
#     node = find_node_by_mac(drive_to_put[0])    
#     node.send(data)
#     if len(all_macs) >=3:
#         all_drives = [drive if drive[0] in all_macs else None for drive in Drives.get_all_drives()]
#         if len(all_drives) > 3:
#             drives = give_drivers(drive_to_put,all_drives)
#             create_parity(drives)

def get_object_from_rb(obj_id:int):
    t_obj = None
    for obj in get_objects():
        if id(obj) == obj_id:
            t_obj = obj
            break
    if t_obj is None: ObjectNotFoundInRecycleBean()
    return t_obj

def handle_chuncked_data(msg: Message):
    if len(msg.data) == 1:
        raise Exception(f"error in client while sending drive: CLOSE RECIVING Q THREAD!!!: {msg.data[0].decode()}")
    q_id = loads(msg.data[0])
    mac = msg.data[1].decode()
    drive_name  = msg.data[2].decode()
    q = None
    for obj in get_objects():
        if id(obj) == q_id:
            q = obj
            break
    if q is None: raise ObjectNotFoundInRecycleBean('Could not find q object')
    while q.qsize() > 5:
        continue
    q.put((drive_name,mac, unpack('?',msg.data[3])[0], msg.data[6]))    
    done =unpack('?',msg.data[3])[0]
    response = None
    if not done:
        response = Message(Category.Recovering,7,(msg.data[0],msg.data[2],msg.data[5]))
    return response


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
            elif message.opcode == 11:
                existed = unpack('?', message.data[3])[0]
                drive_name = message.data[4].decode()
                size = int(message.data[2].decode())
                mac = sessions[str(node_key)]
                drive_id = Drives.get_drive_by_mac_and_name(mac,drive_name)
                path = message.data[0].decode()
                if not existed:
                    Data.CreateField(path,'parties',drive_id,message.data[1].decode(),size,True)
                elif existed:
                    Data.update_size_by_hash_path_relation(size,path,drive_id,'parties')
                Drives.decrease_left_size(drive_id,size)
            elif message.opcode ==13:
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
                print(req.data)
                # message = request_to_message(req)
                reciver = handle_request_q(req)
            except Exception as err:
                res_data = ('General error', err)
                traceback.print_exc()
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

def get_used_drive(size:int):
     # taking all connected macs
    all_macs_connected = get_all_macs_currently_connected()
    # getting the all drives orderd by size
    all_drives = Drives.get_max_left_drive_and_mac()
    connected_and_not_parity_method = lambda drive: drive[0] in all_macs_connected and not Parties.check_if_parity_drive(drive[1])
    applicable_drives = list(filter(connected_and_not_parity_method,all_drives))
    
    not_used_drives = list(filter(lambda drive: Drives.get_drive_used_size(drive[1])==0, applicable_drives))
    not_used_drives.sort(key= lambda drive: drive[4],reverse=True)
    if len(not_used_drives)>0:
        if not_used_drives[0][4]>= size:
            return not_used_drives[0]
    else:
        if len(applicable_drives) == 0:
            raise NotEnoghDrivesConnected()
        return max(applicable_drives, key= lambda drive: drive[4])
    # for drive in applicable_drives:
    #     if Drives.get_drive_used_size(drive[1])==0:
    #         if size <= drive[4]:

    # drive_id = None
    # drives_mac = None
    # for id, mac in macs_drives_lst:
    #     if mac in all_macs_connected and not Parties.check_if_parity_drive(id):
    #         drive_id = id
    #         drives_mac = mac
    #         break
    # return drive_id, drives_mac

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

def ask_for_data_recovery(node: Node, drive_name:str, pickeld_q_id:bytes):
    zero_index = pack('L',socket.htonl(0))
    msg = Message(Category.Recovering,12,(pickeld_q_id,drive_name,zero_index)) # in client side get by name and mac from db
    node_msg_q = messages_queues[str(hash(node))] 
    node_msg_q.put((msg, 0))

def recover_drive(recover_drive_id:int, result_drive:int):
    real_drive_id, parity_drive_id = Parties.get_connected_drives_to_real(recover_drive_id)
    real_drive = Drives.get_drive_by_id(real_drive_id) 
    parity_drive = Drives.get_drive_by_id(parity_drive_id) 
    real_drive_node = find_node_by_mac(real_drive[0])
    parity_drive_node = find_node_by_mac(parity_drive[0])
    if real_drive_node is None or parity_drive_node is None:
        raise DriveNodeIsNotAvalableToRecover()
    data_queue = Queue()
    pickeld_q_id = dumps(id(data_queue))
    ask_for_data_recovery(parity_drive_node,parity_drive[3],pickeld_q_id) # for parity drive
    ask_for_data_recovery(real_drive_node,real_drive[3],pickeld_q_id)

    file_name = sha256(str(real_drive).encode() + str(parity_drive_node).encode()).hexdigest()
    res = xor_data(data_queue,None,2,file_name)
    return res

def get_all_macs_currently_connected():
    session_locker.acquire()
    all_macs = [sessions[key] for key in sessions]
    session_locker.release()
    return all_macs

def send_file_to_max_drive(file_data:bytes, user_id, file_name):
    # taking the max size drive from the orderd list
    result_data = encrypt_data_by_used_id(user_id,file_data)
    used_drive = get_used_drive(len(result_data))
    if used_drive is None:
            raise NoNodescurrentlyConnected()
    node = find_node_by_mac(used_drive[0])
    Drives.decrease_left_size(used_drive[1],len(result_data))
    data_field = Data.CreateFieldNoPath(user_id.decode(),used_drive[1],sha256(result_data).hexdigest(),len(result_data))
    response = Message(Category.Storage,1,(result_data,data_field.hash_value,file_name,used_drive[3],str(data_field.id_num)))
    # msg = request_to_message(req, used_drive[3], data_id)
    messages_q = messages_queues[str(hash(node))]
    messages_q.put((response, 0))
    return used_drive

def encrypt_data_by_used_id(user_id, data):
    aes_key =  aes_key = User.get_AES_key_by_id(user_id.decode())
    aes_obj = AESCipher(aes_key)
    result = aes_obj.encrypt(data)
    return result

def get_second_drive(drives_list: list):
    second_drive = max(drives_list,key= lambda drive: drive[4])
    drives_list.remove(second_drive)
    return second_drive

def get_parity_drive(drives_list:list):
    filter_method = lambda drive: not Data.check_if_drive_used_for_data(drive[1])
    drives_list_cp = list(filter(filter_method,drives_list.copy()))
    parity_drive = max(drives_list_cp,key= lambda drive: drive[4])
    drives_list.remove(parity_drive)
    return parity_drive

def get_two_max_left_size_drives_from_list(drives_list:list):
    parity_drive = max(drives_list,key= lambda drive: drive[4])
    second_drive = max(drives_list,key= lambda drive: drive[4])
    return second_drive, parity_drive

def find_recover_drive(base_drive_id):
    base_drive_size = Drives.get_drive_used_size(base_drive_id)
    all_macs = get_all_macs_currently_connected()
    filter_method = lambda drive: drive[0] in all_macs and not Parties.check_if_connected(drive[1]) and Drives.get_drive_used_size(drive[1]) ==0 and drive[4]> base_drive_size
    all_drives = Drives.get_all_drives()
    applicable_drives = list(filter(filter_method,all_drives))
    if len(applicable_drives)==0:
        return None
    else:
        return max(applicable_drives,key=lambda drive: drive[4])

def extract_file_name_from_path(path:str):
    path_obj = Path(path)
    file_name = path_obj.name
    return file_name.split('__')[0]

def get_file_obj(file_record):
    return {
        'file name': extract_file_name_from_path(file_record[3]),
        'file hash': file_record[0],
        'path': file_record[3],
        'drive name': Drives.get_drive_by_id(file_record[5])[3],
        'size': file_record[2]
    }

def build_file_tree(drive_id):
    file_records = Data.get_file_records(drive_id)
    return [get_file_obj(file_rec) for file_rec in file_records]

def extract_file_indicies_by_tree(file_path:str, drive_file_tree:list):
    start_location = 0
    for file in drive_file_tree:
        if file['path'] == file_path:
            return start_location, start_location+ file['size']
        else:
            start_location+= file['size']


def get_info(user_id:str):
    users_inf = get_connected_and_signed(len(nodes))
    data_inf = get_data_stats()
    data_spread_inf = Data.get_data_crossing(user_id)
    result = {
        'users info': users_inf,
        'data info': data_inf,
        'data spread' : data_spread_inf
    }
    return result

def check_parity_size(drives:tuple):
    return max([ Drives.get_drive_used_size(drive[1]) for drive in drives])

def update_records(records:tuple)->tuple:
    new_records = []
    for record in records:
        tmp = list(record)
        tmp.insert(2,extract_file_name_from_path(record[1]))
        new_records.append(tuple(tmp))
    return tuple(new_records)
def handle_request_q(req:Query_Request):
    if req.method == Requests.Add_File:
        pure_file_data = req.data[req.data.find(b'*')+1:]
        user_id = bytearray(req.data[:req.data.find(b'*')])
        file_name = req.file_name
        all_drives = Drives.get_all_drives() # wrttien here becuase dont want to handle the change in the left_space filed in the drive
        try:
            used_drive = send_file_to_max_drive(pure_file_data,user_id,file_name)
        except NotenoughSpaceInTheDrive:
            return 'file did not uploaded, there is not enough space in the drive'
        all_macs = get_all_macs_currently_connected()
        # check recover
        all_drives.remove(used_drive)
        filterd_drives = list(filter(lambda drive: drive[0] in all_macs, all_drives))
        if len(filterd_drives) >=2:
            connected_drives = Parties.get_connected_drives_to_real(used_drive[1])
            if connected_drives is None:
                parity_drive = get_parity_drive(filterd_drives)
                second_drive = get_second_drive(filterd_drives)
                if Parties.check_if_connected(second_drive[1]) and Parties.check_if_connected(parity_drive[1]):
                    raise NotEnoghDrivesConnected()
            else:
                second_drive, parity_drive = Drives.get_drive_by_id(connected_drives[0]), Drives.get_drive_by_id(connected_drives[1])
            try:
                sleep(1)
                if Drives.get_drive_used_size(used_drive[1])==0 or Drives.get_drive_used_size(second_drive[1])==0:
                    raise DrivesDontHaveData()
                elif Data.check_if_drive_used_for_data(parity_drive[1]):
                    raise NotEnoghDrivesConnected()
                if check_parity_size((used_drive, second_drive)) >parity_drive[4]:
                    raise NotenoughSpaceInTheDrive()
                create_parity(used_drive,second_drive,parity_drive)
            except NotEnoghDrivesConnected:
                return 'file uploded with no parity drive\nNot enough drives are connected'
            except DrivesDontHaveData:
                return 'file uploded with no parity drive\nDrive dont have data'
            except NotenoughSpaceInTheDrive:
                return 'file uploded with no parity drive\nPareity Drive dont have enough space left'
            return 'file uploded with parity drive'
        return 'file uploded with no parity drive'
    
    elif req.method == Requests.Files_List:
        records = Data.get_data_records()
        records = list(filter(lambda record: not None in record,records))
        return update_records(records)
    
    elif req.method == Requests.Retrive_File:
        file_meta_data = get_file_info(req.file_name)
        file_mac = Drives.get_drive_by_id(file_meta_data.location)[0]
        file_node = find_node_by_mac(file_mac)
        if file_node is None:
            result_drive = find_recover_drive(file_meta_data.location)
            data = recover_drive(file_meta_data.location,result_drive)
            
            if data is not None:
                drive_tree = build_file_tree(file_meta_data.location)
                s,t = extract_file_indicies_by_tree(file_meta_data.path, drive_tree)
                worked = True
                file_data = data[s:t]
            else:
                worked = False
                file_data=b''
        elif file_node is not None:
            worked, file_data = get_file_from_node(file_node, file_meta_data.path)
        if worked:
            aes_key = User.get_AES_key_by_id(file_meta_data.relation)
            aes_manage = AESCipher(aes_key)
            decrypted = aes_manage.decrypt(file_data)
            return decrypted
        else:
            raise UnableToUploadFile(file_data)
    elif req.method == Requests.Info:
        user_name = req.data.decode()
        print(req.data)
        return get_info(user_name)

        
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
                for thread in handle_requests_threads:
                    if not thread.is_alive():
                        handle_requests_threads.remove(thread)

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
        gui_shr = None
        server_sem = None
        threads = []
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
            th = Thread(target=handle_client, args= (soc,))
            th.start()
            threads.append(th)
    except Exception as err:
        print('got error: ',err)
        traceback.print_exc()
    finally:
        if gui_sem is not None:
            del gui_sem
        if gui_shr is not None:
            gui_shr.close()
        if server_socket is not None:
            server_socket.close()
        for th in threads:
            th.join()

            

            
if __name__ == "__main__":
    main(('10.100.102.204',8200))