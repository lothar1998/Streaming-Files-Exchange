import socket
from typing import Dict, List
import queue
from threading import Event

STOP_Q_MSG = "STOP"


# Dict(thread_pool, handler, isBusy, queue, block)
class ServerReceiveModule:
    def __init__(self, client_id, clients_queue: Dict[str, List]):
        self.clients_queue = clients_queue
        self.client_id = client_id
        self.clients_queue[f'{self.client_id}'][3] = queue.Queue()

    def receive_message_form_client(self, client_socket: socket.socket, sender_id):
        data_msg = f'Receiving data from client: id_{self.client_id}'
        client_socket.send(bytes(data_msg, 'utf-8'))

        # Receive data in chunks
        buffer_size = 16
        # take block from sender
        block: Event = self.clients_queue[f'{sender_id}'][4]
        while True:
            data = client_socket.recv(buffer_size)

            # TODO: should wait
            # If didn't get any data from client
            if not len(data):
                return False

            print(f"Received {data}")

            self.clients_queue[f'{self.client_id}'][3].put(data)

            if self.clients_queue[f'{sender_id}'][2]:
                return f'Client with id {sender_id} is Busy'

            block.set()

            if not data:
                print(f"Received whole message from {client_socket}")
                self.clients_queue[f'{self.client_id}'][3].put(STOP_Q_MSG)
                break
