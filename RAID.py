from drives import Drives
from graph import Graph
import ctypes
from functools import reduce
from itertools import combinations
def _write_drives(drive_size,generator, name='drive2'):
    chunk = 10000 # bytes
    with open(name,'ab') as file:
        for block in range(drive_size//chunk):
            file.write(generator(chunk))


def find_comd(drives):
    pass

def build_grpah(drives:list)-> Graph:
    graph = Graph(len(drives))
    for i in range(len(drives)):
        for j in range(i, len(drives)):
            try:
                if drives[i][0] != drives[j][0]:
                    graph.add_edge(i, j)
            except ValueError as err:
                print(err)
                continue
            # if drives[i]
    return graph

def get_combs(graph:Graph):
    combs = {}
    for w in range(graph.size):
        combs[str(w)] = []
        for h in range(w,graph.size):
            if graph[w,h] == 1:
                combs[str(w)].append(h)
        combs[str(w)] = tuple(combs[str(w)])
    return combs
      
def get_effiency(drives:list):
    rotate_list = lambda list_data, times: list_data[times:] + list_data[:times]
    if not len(drives) == 3:
        raise ValueError('Len must be 3')
    combs = []
    for i in range(1,4):
        rotated = rotate_list(drives,i)
        eff = rotated[2][4] - max(rotated[0][4],rotated[1][4]) 
        if eff >= 0 :
            combs.append((rotated, eff))
    red_func = lambda d_1, d_2: d_1 if d_1[1] < d_2[1] else d_2
    return reduce(red_func,combs)
    

def get_allocated_drives(sessions: dict)-> tuple:
    """
    gives you drives that are currently avalable for raid
    :param nodes is the list of all nodes connected currently
    :returns a tuple holding sub tuple wich contains ((drive_id):str, parity:bool...)
    """
    # find 3 drives that:
    # 1. are in macs list
    # 2. the max left_space of the 2 drives is min in the third
    macs = [sessions[key] for key in sessions]
    drives = Drives.get_all_drives()
    check_drive = lambda drive: drive if drive[0] in macs else None
    macs_drives = [ check_drive(drive) for drive in drives]
    print(macs_drives)
    graph = build_grpah(macs_drives)
    print(graph)
    coms = get_combs(graph)
    greateset = []
    for drive in coms:
        all_combs = list(combinations(coms[drive],2))
        effences =[]
        for comb in all_combs:
            effences.append(get_effiency([macs_drives[int(drive)], macs_drives[comb[0]],macs_drives[comb[1]]]))
        if len(effences)>0:
            val = min(effences, key=lambda eff: eff[1])
            greateset.append(val)
    val = min(greateset, key=lambda eff: eff[1])
    return val
    
def check_used(drive_mac: str):
    pass
def give_drivers(driver, drives:list):
    for dr in drives:
        if dr[0] == driver[0]:
            drives.remove(dr)
    #BUG: the left space filed in the drive is related as the occuipied space
    # drives.sort(key=lambda test_driver: test_driver[4])
    #TODO: upgrade so the drives that are returend would be similer in occupied space
    return drives
    # min_driver1 = min(drivers, key=lambda test_driver: test_driver[4])
    # drivers.remove(min_driver1)
    # min_driver2 = min(drivers, key=lambda test_driver: test_driver[4])
    # drivers.remove(min_driver2)
    # return min_driver1, min_driver2

def xor_buffers(res_tup:tuple):
    xor_dll = ctypes.CDLL('E:/YUDB/project/RAID-Store/test_pickeld_q/xor_dll.dll')  # Use example.dll on Windows
    # Define the function prototype
    xor_dll.xor_buffers.restype = None
    xor_dll.xor_buffers.argtypes = [ctypes.POINTER(ctypes.POINTER(ctypes.c_ubyte)), ctypes.c_size_t, ctypes.c_size_t, ctypes.POINTER(ctypes.c_ubyte)]
    res = convert_buffers(res_tup)
    result = (ctypes.c_ubyte * len(res_tup[1]))()
    xor_dll.xor_buffers(res, ctypes.c_size_t(len(res_tup)), ctypes.c_size_t(len(res_tup[0])), result)
    return bytes(result)


def convert_buffer(buffer:bytes):
    return (ctypes.c_ubyte * len(buffer)).from_buffer_copy(buffer)

def convert_buffers(buffers:tuple):
    pointer_array = (ctypes.POINTER(ctypes.c_ubyte) * len(buffers))()
    for index, buffer in zip(range(len(buffers)),buffers):
        pointer_array[index] = ctypes.cast(buffer, ctypes.POINTER(ctypes.c_ubyte))
    return pointer_array 

def convert_bytes(bytes_tuple: tuple):
    conv_tup = []
    for buf in bytes_tuple:
        conv_tup.append(convert_buffer(buf))
    return convert_buffers(tuple(conv_tup))

if __name__ == "__main__":
    sessions= { 
        '1':'0xccd9ac32d1f5',
        '2':'0xccd9ac32d1f6',
        '3':'0xccd9ac32d1f7',
        '4':'0xccd9ac32d1f5',
        '5':'0xccd9ac32d1f6',
        '6':'0xccd9ac32d1f7',
        '7':'0xccd9ac32d1f7',
        '8':'0xccd9ac32d1f7',
        '9':'0x10101010000',
    }

