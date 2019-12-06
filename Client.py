import socket
import concurrent.futures
import threading
import time


def parse_first_msg(data):
    client_id, file_name = data.split(sep=';')
    return client_id, file_name


def sender_thread(client):
    while True:
        client.condition_send.wait()

        if client.is_finished:
            break

        to_send = str(client.client_receiver_id) + ";" + str(client.file_path)
        client.client_socket.send(to_send.encode())

        client.condition_send.clear()
        client.condition_send.wait()

        if not client.is_receiver_client_busy:
            file = open(client.file_path, "r")
            line = file.readline()
            while line:
                client.client_socket.send(line.encode())
                line = file.readline()

        client.condition_send.clear()


def receiver_thread(client):
    while True:
        if client.is_finished:
            break
        data = client.client_socket.recv(16)
        data = data.decode()
        if data == "BUSY":
            client.is_receiver_client_busy = True
            client.condition_send.set()
        elif data == "NOT_BUSY":
            client.is_receiver_client_busy = False
            client.condition_send.set()
        else:
            (client_id, file_name) = parse_first_msg(data)
            print(client_id)
            print(file_name)
            file = open(file_name, "a+")
            while True:
                data = client.client_socket.recv(16).decode()
                if data == "END":
                    break
                file.write(data)
            file.close()


class Client:
    def __init__(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port
        self.client_socket = None
        self.thread_pool = None
        self.file_path = None
        self.condition_send = threading.Event()
        self.condition_recv = threading.Event()
        self.is_finished = False
        self.is_ready_to_receive = False
        self.client_receiver_id = None
        self.is_receiver_client_busy = False

    def initiate_connection(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_SCTP)
        self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.client_socket.connect((self.ip_address, self.port))
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(2, thread_name_prefix="Client module")
        self.thread_pool.submit(sender_thread, self)
        self.thread_pool.submit(receiver_thread, self)

    def send_file(self, file_path, client_receiver_id):  # should be locked to end of communication
        self.file_path = file_path
        self.client_receiver_id = client_receiver_id
        self.condition_send.set()

    def close_connection(self):
        self.is_finished = True
        self.condition_send.set()
        self.condition_recv.set()
        self.thread_pool.shutdown(False)
        self.client_socket.shutdown(socket.SHUT_RDWR)
        self.client_socket.close()


if __name__ == "__main__":
    client_module = Client("127.0.0.1", 6969)
    client_module.initiate_connection()
    time.sleep(3)
    client_module.send_file("README.md", 69571)
    time.sleep(100)
    client_module.close_connection()
