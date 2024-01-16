import socket
from typing import  Tuple
from threading import Thread
from Message import Message
from node import Node

# global vars
running = True


def build_response(message: Message):
    match (message.category):
        case
def handle_client(client_soc: socket.socket):
    end_point = Node(client_soc)
    while running:
        message = end_point.recive()
        res = build_response(message)
        end_point.send(res)



def main(creds: Tuple(str, int )):
    global running
    server_socket = socket.socket()
    server_socket.bind(creds)
    server_socket.listen(5)
    while running:
        addr, soc = server_socket.accept()
        print('new connection from: '+addr)
        threads = []
        th = Thread(target=handle_client, args= (soc,))
        th.start()
        threads.append(th)
    for th in threads:
        th.join()
        
            

            

         

if __name__ == "__main__":
    main()