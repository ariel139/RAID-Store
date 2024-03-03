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
from Query_Request import Query, DEFAULT_SIZE
from SharedMemory import SharedMemory
from drives import Drives
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
            pass
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

def request_to_message(req:Query)-> Message:
    match (req.method):
        case Requests.Add:
            request_data = req.data
            #TODO: add reed-solomon 
            return Message(Category.Storage,1,(request_data,))
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
        req = Query.analyze_request(shr)
        message = request_to_message(req)
        reciver = get_reciver(req)
        messages_q = messages_queues[hash(reciver)]
        messages_q.put((message, 0)) # might need a lock

def get_reciver(req:Query):
    if req.method == Requests.Add:
        wanted_macs = Drives.get_lowest_drive_mac()
        for mac in wanted_macs:
            node_found = find_node_by_mac(mac)
            if node_found is not None:
                return node_found
        raise NoNodescurrentluConnected()
        # get from nodes the ids and then get the desierd drive to add
    else:
        raise NotImplementedError("get node from params")
        
def find_node_by_mac(mac:str) -> Node:
    node_keys = [(hash(node),node) for node in nodes]
    for key in node_keys:
        if sessions[str(key[0])] == mac:
            return key[1]
    return None
def handle_client(client_soc: socket.socket):
    global nodes
    try:
        end_point = Node(client_soc)
        nodes.append(end_point)
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
    main(('127.0.0.1',8200))