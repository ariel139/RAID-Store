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
MAX_SUB_THREADS = 5
SIGNAL_SEMAPHORE_NAME = 'sem_signal'
SHARED_MEMORY_NAME ='shared_memory'

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
    slicer_index = len(min(drives_buffers.items(), key = lambda value: len(value[1]))[1])
    to_xor = [buf[1][:slicer_index] for buf in drives_buffers.items()]
    for i in drives_buffers.keys():
        drives_buffers[i] = drives_buffers[i][slicer_index:]
    return xor_buffers(tuple(to_xor))

def xor_data(q: Queue, res_drive: tuple)->bytes:
    drives_buffers = {}
    parity_node = find_node_by_mac(res_drive[0])
    dones = []
    while True:
        drive_info, data,done = q.get()
        if done:
            dones.append(drive_info)
        if drive_info in drives_buffers.keys():
            drives_buffers[drive_info]+=data
        else: drives_buffers[drive_info] = data
        if drive_info in drives_buffers.keys():
            if drive_info in dones and len(drives_buffers[drive_info]) == 0:
                del drives_buffers[drive_info]
        xord_data_buffer = xor_drives(drives_buffers)
        if xord_data_buffer is not None:
            parity_node.send(xord_data_buffer)
        if len(drives_buffers.keys()) == 0:
            break


def create_parity(drives:list):
    # d_1 + d_2 are getting xor'd
    #d_3 get the result
    result_drive = max(drives, key= lambda drive: drive[4])
    nodes = []
    for drive in drives:
        nodes.append(find_node_by_mac(drive[0]))
    reciving_q = Queue()
    pickeld_q_id = dumps(id(reciving_q))
        # messages_q.put((message, 0)) # might need a lock
    for node,drive in zip(nodes,drives):
        node_msg_q = messages_queues[hash(node)]
        msg = Message(Category.Recovering,7,(pickeld_q_id,drive[3])) # in client side get by name and mac from db
        node_msg_q.put((0,msg))
    xor_data(reciving_q, result_drive)
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
        drives = give_drivers(drive_to_put,all_drives)
        create_parity(drives)

def handle_chuncked_data(msg: Message):
    q_id = loads(msg.data[0].decode())
    drive_id  = msg.data[1].decode()
    q = None
    for obj in get_objects():
        if id(obj) == q_id:
            q = obj
            break
    if q is None: raise QueueObjectNotFound('Could not find q object')
    q.put((drive_id, msg.data[1]))
    return Message(Category.Recovering,9,(msg.data[0],msg.data[1]))


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
            if message.opcode == 7:
                mac = sessions[str(node_key)]
                try:
                    Drives(mac,message.data[0],message.data[1],message.data[2])
                    return Message(Category.Storage,8)
                except SumOfDrivesIncompitable:
                    return Message(Category.Errors,5,'The size of the drive is to high from the space you granted, add more space before')
                except DeviceAlreadyExsits:
                    return Message(Category.Errors,6,)   
        case Category.Recovering:
            if message.opcode == 8:
                return handle_chuncked_data(message)
        case Category.Errors:
            #may not be used
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

def request_to_message(req:Query_Request, *args)-> Message:
    match (req.method):
        case Requests.Add:
            file_data = req.data
            file_name = req.file_name
            file_hash = sha256(file_data).hexdigest()
            if isinstance(args[0], str):
                desierd_drive = args[0].encode()
            #TODO: add reed-solomon 
            return Message(Category.Storage,1,(file_data,file_hash,file_name, desierd_drive))
            # add file
            pass 
        case Requests.Delete:
            # make sure to retrive file path and other importent parameters
            return Message(Category.Storage,3,)
            # delete file
        case Requests.Retrive:
            # retrive file for client
            pass
        case _:
            # error
            pass

def get_gui_requests(sem:Semaphore,shr:SharedMemory):
    global running
    while running:
        sem.acquire()
        req = Query_Request.analyze_request(shr)
        # message = request_to_message(req)
        reciver = handle_request_q(req)
        # messages_q = messages_queues[hash(reciver)]
        # messages_q.put((message, 0)) # might need a lock

def handle_request_q(req:Query_Request):
    if req.method == Requests.Add:
        session_locker.acquire()
        all_macs = [sessions[key] for key in sessions]
        session_locker.release()
        macs_drives_lst = Drives.get_max_left_drive_and_mac()
        drive_id = None
        drives_mac = None
        for id, mac in macs_drives_lst:
            if mac in all_macs:
                drive_id = id
                drives_mac = mac
                break
        if drive_id is None and drives_mac is None:
            print('NoNodescurrentlyConnected()') #TODO: handle response to gui
            return
        node = find_node_by_mac(drives_mac)
        drive = Drives.get_drive_by_id(drive_id)
        msg = request_to_message(req, drive[3])
        messages_q = messages_queues[str(hash(node))]
        messages_q.put((msg, 0)) # might need a lock
        # get from nodes the ids and then get the desierd drive to add
        if len(all_macs) >=3:
            all_drives = [drive if drive[0] in all_macs else None for drive in Drives.get_all_drives()]
            drives = give_drivers(Drives.get_drive_by_id(drive_id),all_drives)
            create_parity(drives)
    else:
        raise NotImplementedError("get node from params")
        
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
        server_socket = socket.socket()
        server_socket.bind(creds)
        server_socket.listen(5)
        print('SERVER running...')
        signal_sem = Semaphore(SIGNAL_SEMAPHORE_NAME, initial_value=0)
        shr = SharedMemory(SHARED_MEMORY_NAME,DEFAULT_SIZE)
        gui_thread = Thread(target=get_gui_requests,args=(signal_sem,shr))
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
        del signal_sem
        shr.close()
        server_socket.close()
        for th in threads:
            th.join()

            

            
if __name__ == "__main__":
    main(('10.100.102.204',8200))