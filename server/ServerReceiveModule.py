import socket
from typing import Dict
import queue


class ServerReceiveModule:
    def __init__(self, client_id, clients_queue: Dict[str, queue.Queue]):
        self.client_id = client_id
        self.clients_queue = clients_queue

    def receive_message_form_client(self, client_socket: socket.socket):
        q = queue.Queue(maxsize=1024)
        self.clients_queue[f'{self.client_id}'] = q
        data_msg = f'Receiving data from client: {self.client_id}'
        client_socket.send(bytes(data_msg, 'utf-8'))

        # Receive data in chunks
        full_msg = ''
        buffer_size = 16
        while True:
            data = client_socket.recv(buffer_size)

            # If didn't get any data from client
            if not len(data):
                return False

            self.clients_queue[f'{self.client_id}'].put(data.decode('utf-8'))

            print(f"Received {data}")

            if not data:
                # to logger?
                print(f"Received whole message from {client_socket}")
                self.clients_queue[f'{self.client_id}'].put(None)
                break
