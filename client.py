import socket
SERVER_IP = None #TODO: set default server ip
SERVER_PORT = None # TODO: Set deafult server port

def main():
    client_soc = socket.socket()
    address = (SERVER_IP,SERVER_PORT)
    client_soc.connect(address)
    


if __name__ == "__main__":
    main()