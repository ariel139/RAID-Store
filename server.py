import socket
from typing import  Tuple
from threading import Thread, Lock
from Message import Message
from node import Node
from enums import Countries,Category
from Computers import Computers
from queue import Queue

MAX_SUB_THREADS = 5

# global vars
running = True
sessions = {}
nodes = []
session_locker = Lock()

def handle_request(message: Message, node_key:int):
    global sessions
    match (message.category):
        case Category.Authentication:
            if message.opcode == 1:
                pass # endpoint sign up
            elif message.opcode == 2:
                pass # delete endpoint
            elif message.opcode == 3:
                mac = message.data[0].decode()
                session_locker.acquire()
                sessions[str(node_key)] = mac
                session_locker.release()
                return Message(message.category,message.opcode+3,b'')
            else:
                pass # error
        case Category.Status:
            pass
        case Category.Storage:
            # add disk / storage space
            pass
        case Category.Recovering:
            pass
        case Category.Errors:
            pass
        case _:
            pass
            #default

def handle_requests(message: Message, q: Queue, key:int, id: str):
    res = handle_request(message, key)
    q.put((res,id))

def send_messages(node: Node, q: Queue):
    while True:
        message, id = q.get()
        if message == 'stop':
            break
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


def main(creds: Tuple[str, int ]):
    global running
    server_socket = socket.socket()
    server_socket.bind(creds)
    server_socket.listen(5)
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