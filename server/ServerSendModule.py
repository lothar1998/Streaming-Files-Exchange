from typing import Dict, List
import concurrent.futures


class ServerSendModule:
    def __init__(self, ip_address, port, client_socket, clients_queue: Dict[str, List], client_address, client_id):
        self.client_id = client_id
        self.ip_address = ip_address
        self.port = port
        self.client_socket = client_socket
        self.clients_queue = clients_queue
        self.client_address = client_address
        self.thread_pool = None

    def send_message_to_client(self, sender_id, receiver_id, file_to_send):
        # set this client Busy
        cli_info = f"Client with ip {self.client_address} and id: {sender_id} has connected to the server"

        self.client_socket.send(bytes(cli_info, 'utf-8'))

        # check if client is busy
        if self.clients_queue[f'{receiver_id}'][2]:
            print(f"Client_{receiver_id} is Busy")
            return False

        # set sender_id and get queue
        receiver_q = self.clients_queue[f'{receiver_id}'][1](sender_id)

        receiver_q.put(file_to_send)

        print("Loaded whole file bytes to queue")
        receiver_q.put(None)

        # Unlock this client
        self.clients_queue[f'{self.clients_queue}'][2] = False

    def thread_queue_handler(self, other_cli_id):
        self.clients_queue[f'{self.clients_queue}'][2] = True
        self.clients_queue[f'{self.client_id}'][3] = self.clients_queue[f'{other_cli_id}'][3]
        q = self.clients_queue[f'{self.client_id}'][3]
        while True:
            data = q.get()
            self.client_socket.send(data)
            if data is None:
                msg = f'Received full data'
                self.client_socket.send(bytes(msg, 'utf-8'))
                self.clients_queue[f'{self.clients_queue}'][2] = False
