import socket
import queue
from typing import Dict, List


# Dict(thread_pool, isBusy, queue)
class ServerReceiverModule:
    def __init__(self, client_id, clients_dict: Dict[str, List], client_socket):
        self.client_id = client_id
        self.clients_dict = clients_dict
        self.client_socket: socket.socket = client_socket

    @staticmethod
    def parse_msg(data):
        return data.split(sep=';')

    def receive_data(self):
        while True:
            q: queue.Queue = self.clients_dict[f'{self.client_id}'][2]
            data = q.get()
            cli_2_id, file_name = self.parse_msg(data)

            cli_2_data: list = self.clients_dict[f'{cli_2_id}']

            if cli_2_data[1]:
                this_cli_q: queue.Queue = self.clients_dict[f'{self.client_id}'][2]
                this_cli_q.put('BUSY')
                continue
            else:
                this_cli_q: queue.Queue = self.clients_dict[f'{self.client_id}'][2]
                this_cli_q.put('NOT_BUSY')

                buffer_size = 16
                while True:
                    data = self.client_socket.recv(buffer_size).decode('utf-8')
                    cli_2_data[2].put(data)
                    if data == 'END':
                        break
