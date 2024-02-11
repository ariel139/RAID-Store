import socket
from node import Node
from Message import Message
from enums import *
import server_Exceptions
from uuid import getnode # for mac adress

# constants
SERVER_IP = '127.0.0.1' #TODO: set default server ip
SERVER_PORT = 8200 # TODO: Set deafult server port
MAC = hex(getnode()).encode()# TODO: set it later
FREE_SPACE = 100000 # b'\xa0\x86\x01' in bytes
LOCATION = Countries.Afghanistan

def init_sign_in(server: Node):
    sign_in_message = Message(Category.Authentication,3,(MAC,))
    server.send(sign_in_message)
    while True:
        response, id = server.recive()
        try:
            if Category(response.category) == Category.Errors:
                raise server_exceptions[str(response.opcode)]  
            elif response.opcode == 5 and Category(response.category) == Category.Authentication:
                print('connected')
                break
            else:
                raise server_Exceptions.GeneralError('Unknowun error eccourd in the server side')    
        except server_Exceptions.UserAlreadyExsit:
            print('The user with the mac adress = '+ MAC.decode()+ ' is already in our system ty again later')
            break
        except server_Exceptions.UserDoesNotExsit:
            sign_up = Message(Category.Authentication,1,(MAC,str(FREE_SPACE), str(LOCATION.value[0])))
            server.send(sign_up)
        
def handle_node_asks():
    menu = """What Do You Wish To DO:
    0. exit
    1. delete this pc from the network
    2. add storage to the network
    """
    print(menu)
    res = input('Enter your answer: ')
    match(res):
        case '0':
            return Message(Category.Status,2)
                # close all
        case '1':
            return Message(Category.Authentication,2)
            # delete pc
        case '2':
            #TODO: MAYBE: check if there is enough space in the PC
            size = input('Enter amount of bytes you can allocate:')
            check_str = size[1:] if size[0] == '-' else size
            if not check_str.isnumeric():
                print('invalid size')
            return Message(Category.Storage,0,(size,))
            # add storage
        case _:
            print('Invalid answer')                    
        
def handle_request(node: Node, response: Message):
    #TODO: handle id
    node.send(response)
    response, id = node.recive()
    if Category(response.category) == Category.Errors:
        if response.opcode == 5:
            raise Exception(response.data[0])
        raise server_exceptions[str(response.opcode)]
    else:
        return response
    # later handle exceptions


def main():
    client_soc = socket.socket()
    address = (SERVER_IP,SERVER_PORT)
    client_soc.connect(address)
    node = Node(client_soc)
    init_sign_in(node)
    #TODO: add the threads shit
    while True:
        msg = handle_node_asks()
        res = handle_request(node,msg)
        print(client_out_puts[Category(res.category).name][str(res.opcode)])






if __name__ == "__main__":
    main()