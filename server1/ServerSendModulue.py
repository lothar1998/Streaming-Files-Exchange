from typing import Dict, List
import socket


# Dict(thread_pool, isBusy, queue)
class ServerSendModule:
    def __init__(self, client_id, clients_dict: Dict[str, List], client_socket):
        self.client_id = client_id
        self.clients_dict = clients_dict
        self.client_socket: socket.socket = client_socket

    def _send_to_client(self):
        while True:
            data = self.clients_dict[self.client_id][2].get()
            self.client_socket.send(data.encode())

    def execute(self):
        self._send_to_client()
