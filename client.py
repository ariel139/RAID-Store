import socket
from node import Node
from Message import Message
from enums import Category, Countries
import server_Exceptions
SERVER_IP = '127.0.0.1' #TODO: set default server ip
SERVER_PORT = 8200 # TODO: Set deafult server port
MAC = None # TODO: set it later
FREE_SPACE = 100000 # in bytes
LOCATION = Countries.Afghanistan
def init_sign_in(server: Node):
    try:
        sign_in_message = Message(Category.Authentication,3,(MAC,))
        server.send(sign_in_message)
    except server_Exceptions.UserDoesNotExsit:
        sign_up = Message(Category.Authentication,1,(MAC,FREE_SPACE, LOCATION))
        server.send(sign_up)
    response = server.recive()
    if not(response.opcode == 4 and response.category == Category.Authentication):
        raise server_Exceptions.GeneralError


def main():
    client_soc = socket.socket()
    address = (SERVER_IP,SERVER_PORT)
    client_soc.connect(address)
    node = Node(client_soc)
    init_sign_in(node)


    


if __name__ == "__main__":
    main()