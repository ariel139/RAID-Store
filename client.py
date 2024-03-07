import socket
from node import Node
from Message import Message
from enums import *
import server_Exceptions
from uuid import getnode # for mac adress
from threading import Thread
from wmi import WMI
# constants
SERVER_IP = '127.0.0.1' #TODO: set default server ip
SERVER_PORT = 8200 # TODO: Set deafult server port
MAC = hex(getnode()).encode()# TODO: set it later
print(MAC)
FREE_SPACE = 100000 # b'\xa0\x86\x01' in bytes
LOCATION = Countries.Afghanistan

#global vars
RUNNING = True
client_asks = [] # list holding the ids of messages of clients asks


def get_physical_drives():
    c = WMI()
    physical_drives = c.Win32_DiskDrive()
    drive_info = []
    for drive in physical_drives:
        drive_info.append({
            'Name': drive.Name,
            'model': drive.Model,
            'interface_type': drive.InterfaceType,
        })
    return drive_info 

def choose_drive():
    drives = get_physical_drives()
    print('Choose the drive you want for the size to be added:')
    for drive in drives:
        print(f"{drives.index(drive)+1})\nDevice ID: {drive['Name']} \n    Model: {drive['model']} \n     Interface Type: {drive['interface_type']}")
    drive_index = input('Drive number: ')
    if drive_index.isnumeric() and int(drive_index) >0 and int(drive_index)<= len(drives):
        drive_index = int(drive_index)-1
        return drives[drive_index]
    return None
    

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
        
def handle_node_asks(node: Node):
    global RUNNING, client_asks
    menu = """What Do You Wish To DO:
    0. exit
    1. delete this pc from the network
    2. add storage to the network
    3. add drive to storage space
    """
    print(menu)
    res = input('Enter your answer: ')
    match(res):
        case '0':
            RUNNING = False
            request = Message(Category.Status,2)
                # close all
        case '1':
            request = Message(Category.Authentication,2)
            # delete pc
        case '2':
            #TODO: MAYBE: check if there is enough space in the PC
            size = input('Enter amount of bytes you can allocate:')
            if size !='':
                check_str = size[1:] if size[0] == '-' else size
                if check_str.isnumeric():
                    request = Message(Category.Storage,0,(size,))
            else:
                print('invalid Input')
                request = None
            print('WARNING: the storage system is un-usable until adding drives')
            # add storage
        case '3':
            size = input('Enter amount of bytes you can allocate:')
            drive = choose_drive()
            if drive is None:
                print('invalid Input')
                request = None
            elif size.isnumeric():
               # not sure if working
               drive_type =drive_types[drive['interface_type']]
               request = Message(Category.Storage,7,(drive_type.value,drive['Name'],size))
            else:
                request = None
                print('Invalid answer')   
        case _:
            request = None
            print('Invalid answer') 
    if request is not None:
        id = node.send(request)
        client_asks.append(id)

        
def handle_exceptions(response: Message):
    #TODO: handle id
    if Category(response.category) == Category.Errors:
        if response.opcode == 5:
            raise Exception(response.data[0])
        raise server_exceptions[str(response.opcode)]
    else:
        return response
    # later handle exceptions

def handle_mesage(id, message: Message):
    if id in client_asks:
        print(client_out_puts[Category(message.category).name][str(message.opcode)])
        #TODO: add buffer so the stdout and in wont mess up
        client_asks.remove(id)
    else:
        # make sure the message is recived once you have a connection
        print('message recivesd')
        
    
def handle_server_requests(node: Node):
    while RUNNING:
        request, id = node.recive()
        try:
            res = handle_exceptions(request)
            handle_mesage(id,res)
        except Exception as err:
            print(err.__class__.__name__)
        # handle in here

def main():
    client_soc = socket.socket()
    address = (SERVER_IP,SERVER_PORT)
    client_soc.connect(address)
    node = Node(client_soc)
    init_sign_in(node)
    #TODO: add the threads shit
    server_reqs_th = Thread(target= handle_server_requests, args=(node,))
    server_reqs_th.start()
    while RUNNING:
        handle_node_asks(node)






if __name__ == "__main__":
    main()