from typing import Dict, List
from threading import Event
from queue import Queue

STOP_Q_MSG = "STOP"


# Dict(thread_pool, handler, isBusy, queue, block)
class ServerSendModule:
    def __init__(self, client_socket, clients_queue: Dict[str, List], client_address, client_id):
        self.client_id = client_id
        self.client_socket = client_socket
        self.clients_queue = clients_queue
        self.client_address = client_address
        self.clients_queue[f'{client_id}'][1] = self.thread_queue_handler
        self.clients_queue[f'{client_id}'][2] = False

    def send_to_client(self, receiver_id, file_name):
        cli_info = f"Client with ip {self.client_address} and id: {self.client_id} has connected to the server"

        self.client_socket.send(bytes(cli_info, 'utf-8'))

        # Run handler
        self.clients_queue[f'{receiver_id}'][1](receiver_id, file_name)

    def thread_queue_handler(self, receiver_id, file_name):
        self.clients_queue[f'{self.client_id}'][3] = self.clients_queue[f'{receiver_id}'][3]
        q: Queue = self.clients_queue[f'{receiver_id}'][3]
        block: Event = self.clients_queue[f'{receiver_id}'][4]
        while True:
            block.wait()
            self.clients_queue[f'{self.clients_queue}'][2] = True
            data = q.get()
            if data == STOP_Q_MSG:
                msg = f'file {file_name} has been sent'
                self.client_socket.send(bytes(msg, 'utf-8'))
                self.client_socket.close()
                block.clear()
                return msg

            self.client_socket.send(bytes(data, 'utf-8'))
            block.clear()
            self.clients_queue[f'{self.clients_queue}'][2] = False
