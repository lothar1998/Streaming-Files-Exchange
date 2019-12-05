import socket
from typing import Dict, List
import queue


class ServerReceiveModule:
    def __init__(self, client_id, clients_queue: Dict[str, List] = None):
        self.clients_queue = None
        self.client_id = client_id
        self.clients_queue[f'{self.client_id}'][3] = queue.Queue()

    def receive_message_form_client(self, client_socket: socket.socket):
        data_msg = f'Receiving data from client: id_{self.client_id}'
        client_socket.send(bytes(data_msg, 'utf-8'))

        # Receive data in chunks
        buffer_size = 16
        while True:
            data = client_socket.recv(buffer_size)

            # If didn't get any data from client
            if not len(data):
                return False

            print(f"Received {data}")

            self.clients_queue[f'{self.client_id}'][3].put(data.decode('utf-8'))

            if not data:
                print(f"Received whole message from {client_socket}")
                self.clients_queue[f'{self.client_id}'][3].put(None)
                break
