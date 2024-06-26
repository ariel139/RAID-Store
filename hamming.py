from bitarray import bitarray
import numpy as np
from typing import Union
from functools import reduce

def numpy_to_bitarray(np_array):
    # Ensure the numpy array contains only 0s and 1s
    assert np.all((np_array == 0) | (np_array == 1)), "Array must contain only binary values (0s and 1s)"
    # Convert numpy array to list
    bit_list = np_array.tolist()
    # Create a bitarray from the list
    bit_array = bitarray(bit_list)  
    return bit_array
def bitarray_to_numpy(bit_array):
    # Convert bitarray to a list of integers
    bit_list = bit_array.tolist()
    # Convert list of integers to a numpy array
    np_array = np.array(bit_list, dtype=np.uint8)  # Use uint8 to save memory
    return np_array

def n_split(block_size, arr:bitarray):
    np_array = bitarray_to_numpy(arr)
    np_array = np_array.reshape(len(arr)//block_size,block_size)
    return numpy_to_bitarray(np_array.T.flatten())

def b_unsplit(block_size, arr):
    np_array = bitarray_to_numpy(arr)
    np_array = np_array.reshape(block_size, len(arr)//block_size)
    return numpy_to_bitarray(np_array.T.flatten())


def hamming_blocks(data:bitarray,r_bits:int=1013):
    res = bitarray()
    for chunk in split_bit_array_to_chunks(data,r_bits):
        res+=hamming_encode(chunk)
    return res


def bytes_to_hamming(data:bytes):
   arr = bitarray()
   arr.frombytes(data)
   return hamming_blocks(arr)

def split_data(data:bitarray,block_size:int=1024):
    return n_split(block_size, data[:len(data)-len(data)%block_size])+data[len(data)-len(data)%block_size:]

def unsplit_data(data:bitarray,block_size:int=1024):
   return b_unsplit(block_size,data[:len(data)-len(data)%block_size])+data[len(data)-len(data)%block_size:]


def split_bit_array_to_chunks(arr:bitarray,chuck_size):
    cnt = 0
    while cnt<len(arr):
        yield arr[cnt:min(chuck_size+cnt,len(arr))]
        cnt+=chuck_size

def decode_hamming(data:bitarray, block_size:int=1024):
    res = bitarray()
    for chunk in split_bit_array_to_chunks(data,block_size):
        try:
            res+=extract_data(chunk)
        except Exception as err:
            return None
    return res.tobytes()

def prepre_data(data:Union[bitarray,bytes],positions:list):
    if isinstance(data,bitarray):
        full_data = data.copy()
    else:
        full_data = bitarray()
        full_data.frombytes(data)
    full_data+= bitarray(len(positions))
    return full_data

def get_positions(data_length:int):
    cnt = 1
    res = [0]
    while cnt<= data_length:
        res.append(cnt)
        cnt<<=1
    return res

def hamming_encode(data:Union[bitarray,bytes]):
    if isinstance(data,bitarray):
        positions = get_positions(len(data))
    elif isinstance(data, bytes):
        positions = get_positions(len(data)*8)
    full_data = prepre_data(data,positions)
    for pos in positions:
        full_data[pos:]>>=1
    for pos, bit in enumerate(full_data[1:],1):
        if pos in positions:
            continue
        for t_pos in positions:
            if t_pos &pos:
                full_data[t_pos]^=bit
        if bit:
            full_data[0]^=1
    return full_data
    
def hamming_decode(data:bitarray):
    xor =lambda x,y:x^y
    pos =  reduce(xor,[i for i, bit in enumerate(data) if bit])
    evency = reduce(xor, data[1:])
    if pos!=0:
        if data[0]==evency:
            return -1 # 2 or more erros
        return pos #single error
    if pos ==0 and data[0] == evency:
        return-2 # no error

def get_plain_data(encoded_data: bitarray):
    cnt = 1
    l = [0]
    while cnt<len(encoded_data):
        l.append(cnt)
        cnt<<=1
    index = 0
    for pos in l:
        del encoded_data[pos-index]
        index+=1
    return encoded_data
    

def extract_data(raw_data:bytes):
    res = hamming_decode(raw_data)
    if res==-1:
        raise Exception('error in 2 or more places')
    elif res == -2:
        return get_plain_data(raw_data)
    elif res is not None: raw_data[res]^=1
    return get_plain_data(raw_data)

class hammingError(Exception):
    pass