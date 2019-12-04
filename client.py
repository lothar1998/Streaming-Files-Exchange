import socket

from pip._vendor.distlib.compat import raw_input

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

HOST = 'localhost'
PORT = 9991

socket.connect((HOST,PORT))
open_flag = socket.recv(4)


if(open_flag == "true"):
    data_to_send = str(raw_input('Napisz cos byku :'))
    data_byte = bytearray(data_to_send, encoding="utf8")
    socket.send(data_byte)
else:
    print('Byku napisal:')
    data = socket.recv(1024)
    print(data)
socket.close()