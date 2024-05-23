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
from os import getcwd, makedirs, scandir
from base64 import b64encode, b64decode
from pathlib import Path
from random_mac_i import get_mac
if platform.system() == 'Windows':
    from wmi import WMI
from json import *
from jqpy import jq
from sys import argv
from mmap import PAGESIZE
from os.path import getsize
from struct import pack, unpack
import os
from filelock import FileLock
import traceback
from info_retrive import get_client_location
lock_path = FileLock("file_path.lock")

# constants
FILES_LOCK=1
DEBUG = True
FILES_PATH = ''
SERVER_IP = '10.100.102.204' #TODO: set default server ip
SERVER_PORT = 8200 # TODO: Set deafult server port
CHUNCK_SIZE = PAGESIZE *100
if DEBUG:
    print(argv)
    if len(argv) >=2:
        MAC = hex(int(argv[1])).encode()
    else:
        MAC = hex(131176846729400).encode()# TODO: set it later
else:
    MAC = hex(getnode()).encode()# TODO: set it later
print(MAC)
FREE_SPACE = 100000 # b'\xa0\x86\x01' in bytes
LOCATION = get_client_location()

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
    #-l
    qury = "lsblk -n -J -l --output NAME,MODEL,TRAN,mountpoint,size"
    lsblk_output = check_output(qury.split(' ')).decode()
    print(lsblk_output)
    formated_output = jq('[.blockdevices[]|select(.mountpoint==null)]',loads(lsblk_output))[0]
    print(formated_output)
    # lsblk_output = lsblk_output.replace('tran','interface_type' )
    return formated_output
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
    global RUNNING, client_asks, DEBUG
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
  
def create_file_sizes_dict(drive_name:str):
    with lock_path:
        with open(FILES_PATH,'r') as file:
            data = load(file)
    dict = []
    for file in data:
        if file['drive name'] == drive_name:
            dict.append({'path': file['path'], 'size':int(file['size'])})
    return dict

def get_data_from_file(path, start_index,end_index=-1):
    with open(path, 'rb') as file:
        full_buffer = file.read()
        if end_index == -1:
            return full_buffer[start_index:]
        return full_buffer[start_index:end_index]


def get_data_chunk(start_index, end_index, drive_name):
    file_sizes = create_file_sizes_dict(drive_name.decode())
    files_sum = 0
    start_indecie = False
    end_indecie= False
    data_stream = b''
    for file in file_sizes:
        size = file['size']
        path = file['path']
        files_sum+=size
        if not start_indecie:
            if start_index < files_sum:
                start_indecie = path, start_index - (files_sum-size)
        if end_index <= files_sum and not end_indecie:
            end_indecie = path, end_index- (files_sum-size)
        if start_indecie and end_indecie:
            if start_indecie[0] == end_indecie[0]:
                return get_data_from_file(start_indecie[0], start_indecie[1],end_indecie[1])
            data_stream += get_data_from_file(end_indecie[0],0,end_indecie[1])
            return data_stream
        if start_indecie and not end_indecie:
            if len(data_stream) ==0:
                data_stream+= get_data_from_file(path,start_indecie[1])
            else:
                data_stream+= get_data_from_file(path,0)
    return data_stream



def get_dir_size(drive_name:str):
    total = 0
    with lock_path:
        with open(FILES_PATH,'r') as file:
            data = load(file)
    for file in data:
        if file['drive name'] == drive_name.decode():
            total+=int(file['size'])
    return total


  
def send_chuncked_drive(q_id, drive_name: str,start_index:int):
    try:
    # data_path = Path(f'{drive_name.decode()}/raid_{drive_name.decode()[:-1]}')
        print(f'mac: {str(MAC)} + drive name: {drive_name}')
        drive_size = get_dir_size(drive_name)
        chunk_data=get_data_chunk(start_index,start_index+CHUNCK_SIZE, drive_name)
        is_done = True if start_index>= drive_size else False # wether its the last chunck in the sequnce
        if drive_size != 0:
            print(f'{start_index} : {start_index+CHUNCK_SIZE} -- {((start_index+CHUNCK_SIZE)/drive_size)*100}%')
        end_index = pack('L',socket.htonl(start_index+CHUNCK_SIZE))
        start_index = pack('L',socket.htonl(start_index))
        msg = Message(Category.Recovering,8,(q_id,MAC,drive_name, pack('?',is_done),start_index,end_index, chunk_data))
    except Exception:
        msg = Message(Category.Recovering,8,(f'error: {traceback.format_exc()}',))
    return msg



def add_meta_data(file_name:str,file_hash:str, path,drive_name:str):
    file_meta_data = {
            'file name': file_name,
            'file hash': file_hash,
            'path': str(path),
            'drive name' : drive_name,
            'size': str(getsize(str(path)))
        }
    try:
        with lock_path:
            with open(FILES_PATH, 'r') as file:
                curr = load(file)
    except JSONDecodeError:
        file_meta_data = [file_meta_data]
    except FileNotFoundError:
        file_meta_data = [file_meta_data]
    else:
        got = False
        for file in curr:
            if file['path'] == file_meta_data['path'] and file_hash == file['file hash']:
                file['size'] = str(int(file['size'])+int(file_meta_data['size']))
                got = True
                break
        if not got:
            curr.append(file_meta_data)
        file_meta_data = curr
    with lock_path:
        with open(FILES_PATH,'w') as file:
            dump(file_meta_data,file, indent=4)
    

def check_if_file_name_exists(file_name:str):
    with lock_path:
        with open(FILES_PATH,'r') as file:
            data = load(file)
    for file in data:
        if file['file name'] == file_name:
            return True
    return False

def save_file(data:bytes, file_name: str, file_hash: str, drive_name:str,parity_file:bool=False) -> Path:
    #TODO: set the deafult directory for file saving on each drive to be: 'raid_{drive name}'
    #TODO: check duplicateds files
    # the file name for each file in the directory will be: sha256(file_name+file_data)
    if parity_file:
        saved_name = file_name + '__' +sha256(file_name.encode()).hexdigest()
    else:
        saved_name = file_name + '__' +sha256(file_name.encode()+data).hexdigest()
    saved_path_directoris = Path(f'{drive_name.decode()}/raid_{drive_name.decode()[:-1]}')
    full_path = Path(f'{drive_name.decode()}/raid_{drive_name.decode()[:-1]}/{saved_name}')
    #TODO: change appropriate full path to linux NOT: sda/raid_sda...
    makedirs(saved_path_directoris, exist_ok=True)
    with open(full_path, 'wb') as file:
        file.write(data)
    add_meta_data(file_name,file_hash,full_path,drive_name.decode())
    return full_path

def get_metadata()->list:
    with lock_path:
        with open(FILES_PATH) as file:
            meta_data = load(file)
    return meta_data

def get_file_data_and_hash(path:str):
    mt_data =get_metadata()
    for file in mt_data:
        if file["path"] == path:
            with open(path, 'rb') as file_desc:
                return file["file hash"],file_desc.read()
    return '',b''
def handle_server_message(message: Message, node: Node):
    match Category(message.category):
        case Category.Storage:
            if message.opcode == 1:
                path_saved = save_file(message.data[0],message.data[2].decode(),message.data[1].decode(),message.data[3])
                return Message(Category.Storage,2,(str(path_saved).encode(),message.data[-1]))
            elif message.opcode == 4:
                file_hash, file_data = get_file_data_and_hash(message.data[0].decode())
                if file_data == b'':
                    return Message(Category.Storage,5,(b'','did not get file',message.data[2],message.data[3]))
                return Message(Category.Storage,5,(file_data,file_hash,message.data[2]))
        case Category.Recovering:
            if message.opcode == 7:
                try:
                    print('got to partiy sending')
                    start_index = socket.ntohl(unpack('L',message.data[2])[0])
                    response =  send_chuncked_drive(message.data[0], message.data[1], start_index)
                    return response
                except FileNotFoundError:
                    print('stopped Disk is empty')
                    return Message(Category.Errors,4,('Disk is Empty'))               
            elif message.opcode == 10:
                file_hash = sha256(message.data[2]).hexdigest()
                file_size = str(len(message.data[2]))
                existed = pack('?', check_if_file_name_exists(message.data[1].decode()))
                path_saved = save_file(message.data[2],message.data[1].decode(),file_hash, message.data[0],True)
                response = Message(Category.Recovering,11,(str(path_saved),file_hash,file_size, existed,message.data[0]))
                print('sent parity Drive from client')
                return response
            elif message.opcode == 12:
                start_index = socket.ntohl(unpack('L',message.data[2])[0])
                response =  send_chuncked_drive(message.data[0], message.data[1], start_index)
                print('(recovery based) sent with start index of '+str(start_index//CHUNCK_SIZE))
                response.opcode = 13
                return response
        case _:
            raise InvalidCategory()
def handle_mesage(id, message: Message, node: Node):
    if id in client_asks:
        print(client_out_puts[Category(message.category).name][str(message.opcode)])
        #TODO: add buffer so the stdout and in wont mess up
        client_asks.remove(id)
    else:
        res = handle_server_message(message, node) # res must be of type message
        node.send(res)
    
def handle_server_requests(node: Node):
    threads = []
    while RUNNING:
        request, id = node.recive()
        try:
            res = handle_exceptions(request)
            if request.opcode in client_blocking_messages[Category(request.category)]:
                handle_mesage(id,res,node)
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
        FILES_PATH = Path(f'{getcwd()}/{MAC.decode()}.json')
    server_reqs_th = Thread(target= handle_server_requests, args=(node,))
    server_reqs_th.start()
    while RUNNING:
        handle_node_asks(node)






if __name__ == "__main__":
    main()