import socket
from node import Node
from client_exceptions import *
from Message import Message
from enums import *
import server_Exceptions
from uuid import getnode # for mac adress
from threading import Thread
from subprocess import check_output
from hashlib import sha256
import platform
from traceback import print_exc
from os import getcwd
from base64 import b64encode, b64decode
from pathlib import Path
if platform.system() == 'Windows':
    from wmi import WMI
from json import *

# constants
FILES_PATH = ''
SERVER_IP = '10.100.102.204' #TODO: set default server ip
SERVER_PORT = 8200 # TODO: Set deafult server port
MAC = hex(getnode()).encode()# TODO: set it later
print(MAC)
FREE_SPACE = 100000 # b'\xa0\x86\x01' in bytes
LOCATION = Countries.Afghanistan

#global vars
RUNNING = True
client_asks = [] # list holding the ids of messages of clients asks


def get_physical_drives_windows():
    c = WMI()
    physical_drives = c.Win32_LogicalDisk()
    drive_info = []
    for drive in physical_drives:
        drive_info.append({
            'name': drive.Name,
            'model': drive.FileSystem,
        })
    return drive_info 

def get_physical_drives_linux():
    lsblk_output = check_output(['lsblk', '-b', '-n', '-J', '--output', 'NAME,MODEL,TRAN']).decode()
    lsblk_output = lsblk_output.replace('tran','interface_type' )
    drives = loads(lsblk_output)['blockdevices']
    return drives
def choose_drive():
    if platform.system() == 'Linux':
        drives = get_physical_drives_linux()
    elif platform.system() == 'Windows':
        drives = get_physical_drives_windows()
    print('Choose the drive you want for the size to be added:')
    for drive in drives:
        print(f'{str(drives.index(drive)+1)})')
        for key, data in drive.items():
            print(f"{key}:  {data}")
    print()
        
    drive_index = input('Drive number: ').strip('\r')
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
    res = input('Enter your answer: ').strip('\r')
    # # print(res.encode())
    # # print('0'.encode())
    # # print(sha256('0'.encode()).hexdigest())
    # # print(sha256(res.encode()).hexdigest())
    # if res == "0":
    #     print('good')
    match res:
        case '0':
            RUNNING = False
            request = Message(Category.Status,2)
                # close all
        case '1':
            request = Message(Category.Authentication,2)
            # delete pc
        case '2':
            #TODO: MAYBE: check if there is enough space in the PC
            size = input('Enter amount of bytes you can allocate:').strip('\r')
            request = None
            if size !='':
                check_str = size[1:] if size[0] == '-' else size
                if check_str.isnumeric():
                    request = Message(Category.Storage,0,(size,))
            else:
                print('invalid Input')
            print('WARNING: the storage system is un-usable until adding drives')
            # add storage
        case '3':
            request = None
            size = input('Enter amount of bytes you can allocate:').strip('\r')
            drive = choose_drive()
            if drive is None:
                print('invalid Input')
            elif size.isnumeric():
               # not sure if working
               drive_type = file_systems.get(drive['model'],DriveTypes.Null)
               request = Message(Category.Storage,7,(drive_type.value,drive['name'],size))
            else:
                print('Invalid answer')   
        case _:
            request = None
            print('Invalid answer, try again') 
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

def check_file_data(file_data:bytes, check_sum: bytes):
    """
    checks if the files data that has recived from the server is not coruptted
    :param file_data the actual data recived
    :check_sum an hash of the data that has recived from the server
    :returns Tuple containing (bool, bytes)-> bool if there was a corupption, bytes for the data
    """
    created_hash = sha256(file_data).hexdigest().encode()
    if created_hash == check_sum:
        return True, file_data
    #check reed-solomon: fix if needed

def send_drive(node: Node, q_id, drive_name: str):
    pass

def add_meta_data(file_name:str,file_hash:str, path):
    with open(FILES_PATH, 'wb') as file:
        file_meta_data = {
            'file name': file_name,
            'file hash': file_hash,
            'path': path
        }
        try:
            curr = load(file)
        except JSONDecodeError:
            file_meta_data = [file_meta_data]
        else:
            curr.append(file_meta_data)
            file_meta_data = curr
        dump(FILES_PATH,file_meta_data)
def save_file(data:bytes, file_name: str, file_hash: str, drive_name:str):
    #TODO: set the deafult directory for file saving on each drive to be: 'raid_{drive name}'
    # the file name for each file in the directory will be: sha256(file_name+B64(file_data))
    saved_name = sha256(file_name+b64encode(data)).hexdigest()
    saved_path = Path(f'{drive_name}/raid_{drive_name}/{saved_name}')
    add_meta_data(file_name,file_hash,saved_path)
    with open(saved_path, 'wb') as file:
        file.write(data)
        
def handle_server_message(message: Message, node: Node):
    match Category(message.category):
        case Category.Storage:
            if message.opcode == 1:
                save_file(message.data[0],message.data[2],message.data[1],message.data[3])
        case Category.Recovering:
            if message.opcode == 7:
                return send_drive(node, message.data[0], message.data[1])
        case _:
            raise InvalidCategory()
def handle_mesage(id, message: Message, node: Node):
    if id in client_asks:
        print(client_out_puts[Category(message.category).name][str(message.opcode)])
        #TODO: add buffer so the stdout and in wont mess up
        client_asks.remove(id)
    else:
        return handle_server_message(message, node)
    
def handle_server_requests(node: Node):
    threads = []
    while RUNNING:
        request, id = node.recive()
        try:
            res = handle_exceptions(request)
            if request.opcode in client_blocking_messages[Category(request.category)]:
                handle_mesage(id,res) 
            else:
                th = Thread(target= handle_mesage, args=(id,request, node))
                th.start()# make a thread for this normaly, only for none blocking funcs
                threads.append(th)
        except Exception as err:
            print_exc()
            print()
            print(err.__class__.__name__)
    for th in threads:
        th.join()
        # handle in here

def main():
    global FILES_PATH
    client_soc = socket.socket()
    address = (SERVER_IP,SERVER_PORT)
    client_soc.connect(address)
    node = Node(client_soc)
    init_sign_in(node)
    # TODO: add the threads shit
    FILES_PATH = input(f'ENTER path to metadata of files JSON (default: {getcwd()}\\{MAC.decode()}.json): ')
    if FILES_PATH == '':
        FILES_PATH = Path(f'{getcwd()}\\{MAC.decode()}.json')
    server_reqs_th = Thread(target= handle_server_requests, args=(node,))
    server_reqs_th.start()
    while RUNNING:
        handle_node_asks(node)






if __name__ == "__main__":
    main()