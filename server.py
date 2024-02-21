import traceback
import socket
from typing import  Tuple
from threading import Thread, Lock
from Message import Message
from node import Node
from enums import Countries,Category
from Computers import Computers
from queue import Queue
from Semaphore import Semaphore
from server_Exceptions import *
from Query_Request import Query, DEFAULT_SIZE
from SharedMemory import SharedMemory
MAX_SUB_THREADS = 5
SIGNAL_SEMAPHORE_NAME = 'sem_signal'
SHARED_MEMORY_NAME ='shared_memory'

# global vars
running = True
sessions = {}
nodes = []
session_locker = Lock()

def lock_session(func):
    def wrapper(*args, **kwargs):
        session_locker.acquire()
        func(*args, **kwargs)
        session_locker.release()
    return wrapper

@ lock_session
def add_seesion(node_key:str, mac:str):
    global sessions
    sessions[node_key] = mac

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
            if message.opcode == 0:
                mac = sessions[str(node_key)]
                pc = Computers.GetComputer(mac)
                try:
                    pc.add_storage(message.data[0])
                except SizeToLow:
                    return Message(Category.Errors,5,'The Size of the messgae is To Low')
                return Message(Category.Storage,6)

            # add disk / storage space
            pass
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
 
    
def handle_client(client_soc: socket.socket):
    global nodes
    try:
        end_point = Node(client_soc)
        nodes.append(end_point)
        send_message_queue = Queue()
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
        for th in handle_requests_threads:
            th.join()


def get_gui_requests(sem:Semaphore,shr:SharedMemory):
    global running
    while running:
        sem.acquire()
        req = Query.analyze_request(shr)
        print(req)


def main(creds: Tuple[str, int ]):
    global running
    server_socket = socket.socket()
    server_socket.bind(creds)
    server_socket.listen(5)
    print('SERVER running...')
    signal_sem = Semaphore(SIGNAL_SEMAPHORE_NAME)
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
    for th in threads:
        th.join()
        
            

            
if __name__ == "__main__":
    main(('127.0.0.1',8200))