from typing import Dict, List
import socket

def file_name_parser(file_name):
    return file_name[file_name.rfind('/') + 1:]


def type_of_message(message):
    return message[0:message.find(':')]


def content_of_message(message):
    return message[message.find(':') + 1:]


# Dict(thread_pool, isBusy, queue)
class ServerSendModule:
    def __init__(self, client_id, clients_dict: Dict[str, List], client_socket):
        self.client_id = client_id
        self.clients_dict = clients_dict
        self.client_socket: socket.socket = client_socket

    def send_data(self):
        while True:
            queue_data = self.clients_dict[self.client_id][2].get()
            try:
                decoded_data = queue_data.decode()

                if type_of_message(decoded_data) == "info":
                    if content_of_message(decoded_data) == "end_busy":
                        self.clients_dict[int(self.client_id)][1] = False

                if type_of_message(decoded_data) == "end":
                    break

                self.client_socket.send(queue_data)

            except (UnicodeDecodeError, AttributeError):
                self.client_socket.send(queue_data)
