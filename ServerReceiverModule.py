import socket
import queue
from typing import Dict, List

BUFFER_SIZE = 102400

def file_name_parser(file_name):
    return file_name[file_name.rfind('/') + 1:]


def type_of_message(message):
    return message[0:message.find(':')]


def content_of_message(message):
    return message[message.find(':') + 1:]


# Dict(thread_pool, isBusy, queue)
class ServerReceiverModule:
    def __init__(self, client_id, clients_dict: Dict[str, List], client_socket):
        self.client_id = client_id
        self.clients_dict = clients_dict
        self.client_socket: socket.socket = client_socket

    def receive_data(self):
        while True:
            received_data = self.client_socket.recv(BUFFER_SIZE)

            try:
                decoded_data = received_data.decode()
                if type_of_message(decoded_data) == "ask":  # required for sending file
                    if len(content_of_message(decoded_data)) != 0:
                        receiver_client_id = int(content_of_message(decoded_data))
                        if receiver_client_id in self.clients_dict.keys():
                            if self.clients_dict[receiver_client_id][1] == True:
                                self.clients_dict[self.client_id][2].put("info:busy".encode())
                            else:
                                self.clients_dict[receiver_client_id][1] = True  # set as busy user
                                self.clients_dict[self.client_id][2].put("info:not_busy".encode())
                                received_data = self.client_socket.recv(BUFFER_SIZE)
                                self.clients_dict[receiver_client_id][2].put(received_data)
                                size = int(content_of_message(received_data.decode()))
                                current_size = 0
                                received_data = self.client_socket.recv(BUFFER_SIZE)
                                self.clients_dict[receiver_client_id][2].put(received_data)

                                while current_size != size:
                                    received_data = self.client_socket.recv(BUFFER_SIZE)
                                    self.clients_dict[receiver_client_id][2].put(received_data)
                                    current_size += len(received_data)

                                self.clients_dict[receiver_client_id][2].put("info:end_busy".encode())
                        else:
                            self.clients_dict[self.client_id][2].put("info:wrong_key".encode())
                    else:
                        self.clients_dict[self.client_id][2].put("info:wrong_key".encode())

                elif type_of_message(decoded_data) == "end":
                    self.clients_dict[self.client_id][2].put(decoded_data.encode())
                    break

            except (UnicodeDecodeError, AttributeError):
                pass
