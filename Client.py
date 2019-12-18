import socket
import concurrent.futures
import threading
import time
import struct


def file_name_parser(file_name):
    return file_name[file_name.rfind('/') + 1:]


def sender_thread(client):
    while True:
        client.condition_send.wait()
        pass
        if client.is_finished:
            con_close = "CON_CLOSE"
            client.client_socket.send(con_close.encode())
            client.client_socket.shutdown(socket.SHUT_RDWR)
            client.client_socket.close()
            break

        to_send = str(client.client_receiver_id)
        client.client_socket.send(to_send.encode())

        client.condition_send.clear()
        client.condition_send.wait()

        if not client.is_receiver_client_busy:
            to_send = str(client.file_path)
            to_send = file_name_parser(to_send)
            client.client_socket.send(to_send.encode())
            file = open(client.file_path, "r")
            line = file.read(16)
            while line:
                client.client_socket.send(line.encode())
                line = file.readline()

            file.close()

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

            file_name = data
            print(file_name)
            file = open(file_name, "a+")
            while True:
                data = client.client_socket.recv(16).decode()
                if data == "END":
                    break
                file.write(data)
            file.close()


def multicast_search():
    test_msg = b"Hello Multicast"
    multicast_group = ('224.1.1.1', 6969)

    multicast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # if no response from server - timeout
    multicast_sock.settimeout(1)
    # ttl setting for messages to not go past local network
    # packet into single byte by struct
    ttl = struct.pack('b', 1)
    multicast_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    try:
        multicast_sock.sendto(test_msg, multicast_group)
        while True:
            try:
                data, server = multicast_sock.recvfrom(16)
            except socket.timeout:
                print('timed out, no more responses')
                break
            else:
                print(f'received server ip {data} from {server}')
                # return server     # returns complete server info (server_ip, port)
                return data         # returns data sent from server -- here localhost ip

    finally:
        print('closing socket')
        multicast_sock.close()


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
        self.client_id = None

    def initiate_connection(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.client_socket.connect((self.ip_address, self.port))
        self.client_id = self.client_socket.recv(16).decode()
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


if __name__ == "__main__":
    server_info = multicast_search()

    client_module = Client(server_info, 6969)
    client_module.initiate_connection()
    time.sleep(3)
    # client_module.send_file("README.md", 90541)
    client_module.close_connection()
