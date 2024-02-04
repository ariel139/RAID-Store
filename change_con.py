import struct
import socket
num = 99
print(num.to_bytes(1,'big'))
# soc = socket.htons(num)
# print(soc)
# packed = struct.pack('H',soc)
# print( packed)
# unpacked = struct.unpack('H',packed)[0]
# un_soc = socket.ntohs(unpacked)
# print(un_soc)