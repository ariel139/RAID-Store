import socket
from node import Node
from Message import Message
from enums import Category, Countries, server_exceptions
import server_Exceptions
from uuid import getnode # for mac adress
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
        
      
       

def main():
    client_soc = socket.socket()
    address = (SERVER_IP,SERVER_PORT)
    client_soc.connect(address)
    node = Node(client_soc)
    init_sign_in(node)


    


if __name__ == "__main__":
    main()