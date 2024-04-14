PATH = 'used_macs'
import random
from uuid import getnode
def get_macs():
    with open(PATH,'r') as file:
        macs = file.read().split('\n')
    return macs

def generate_random_mac():
    mac = [random.randint(0x00, 0xff) for _ in range(6)]  # Generate 6 random bytes
    formatted_mac = ':'.join(map(lambda x: "%02x" % x, mac))  # Convert bytes to hexadecimal and format as MAC address
    return formatted_mac

def convert_mac(mac):
    return ':'.join(['{:02x}'.format((mac >> ele) & 0xff) for ele in range(0,8*6,8)][::-1])

def get_mac()->str:
    mac = generate_random_mac()
    mac_list = get_macs()
    while mac in mac_list:
        mac = generate_random_mac()
    with open(PATH,'a') as file:
        file.write(mac+'\n')
    return mac

if __name__ == "__main__":
    print(f'Randomed mac: {get_mac()}')
        