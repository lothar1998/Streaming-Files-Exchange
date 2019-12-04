import socket

first_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

HOST = 'localhost'
PORT = 9991

print('Server started!')
print('Waiting for clients...')

first_socket.bind((HOST, PORT))
first_socket.listen(2)

client, addr = first_socket.accept()
print(str(addr) + ' has connected! ')
client.send("true".encode());

client2, addr2 = first_socket.accept()
print(str(addr2) + ' has connected! ')
client2.send("ffff".encode());

message = client.recv(1024)
client2.send(message)

client.close()
client2.close()