import ctypes
import numpy as np
import gc
# Load the shared library
xor_dll = ctypes.CDLL('E:/YUDB/project/RAID-Store/test_pickeld_q/xor_dll.dll')  # Use example.dll on Windows
# Define the function prototype
xor_dll.xor_buffers.restype = None
xor_dll.xor_buffers.argtypes = [ctypes.POINTER(ctypes.POINTER(ctypes.c_ubyte)), ctypes.c_size_t, ctypes.c_size_t, ctypes.POINTER(ctypes.c_ubyte)]

# Example buffers

b_1 = b'\x01\x34\x56\x78'
byte_array = (ctypes.c_ubyte * len(b_1)).from_buffer_copy(b_1)
buffer1 = (ctypes.c_ubyte * 4)(0x1, 0x34, 0x56, 0x78)
buffer2 = (ctypes.c_ubyte * 4)(0xAB, 0xCD, 0xEF, 0x01)
buffer3 = (ctypes.c_ubyte * 4)(0x11, 0x22, 0x33, 0x44)

# Array of buffer pointers
buffers = (ctypes.POINTER(ctypes.c_ubyte) * 3)(byte_array, buffer2, buffer3)
print(type(buffers))
# Allocate memory for the result buffer
result_size = ctypes.sizeof(buffer1)
result = (ctypes.c_ubyte * result_size)()

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
# Call the DLL function
# buf_tup = (b'\x01\x34\x56\x78', b'\xAB\xCD\xEF\x01', b'\x11\x22\x33\x44')
# res = convert_bytes(buf_tup)
# xor_dll.xor_buffers(res, ctypes.c_size_t(3), ctypes.c_size_t(result_size), result)

# # Print the result
# print("XOR result:", end=" ")
# for byte in result:
#     print(f"{byte:02X}", end=" ")
# print()
r_obj = 'did not get'
print(gc.get_count())
for obj in gc.get_objects():
    if id(obj) == 1888064340944:
        r_obj = obj
        break
print(r_obj)