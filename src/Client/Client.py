import socket
import concurrent.futures
import threading
import os
import time
import struct

BUFFER_SIZE = 102400


def file_name_parser(file_name):
    return file_name[file_name.rfind('/') + 1:]


def type_of_message(message):
    return message[0:message.find(':')]


def content_of_message(message):
    return message[message.find(':') + 1:]


def sender_thread(client):
    while True:
        client.condition_send.wait()

        if client.is_finished:  # if client is closed
            break

        if client.client_receiver_id is not None:  # passed client2 id
            # sending request for checking whether client2 is busy
            client.client_socket.send(str("ask:" + str(client.client_receiver_id)).encode('utf-8'))

            client.condition_busy.clear()  # waiting for checking whether client2 is busy
            client.condition_busy.wait()

            if not client.is_receiver_client_busy:
                file_path = str(client.file_path)
                size = os.path.getsize(file_path)
                file_name = file_name_parser(file_path)
                client.client_socket.send(str("size:" + str(size)).encode('utf-8'))  # sending size of file
                client.client_socket.send(str("name:" + str(file_name)).encode('utf-8'))  # sending file name

                current_size = 0
                with open(file_path, "rb") as file:
                    for line in file:
                        if client.sending_interrupted:
                            client.client_socket.send("info:interrupted".encode('utf-8'))
                            client.sending_interrupted = False
                            break
                        client.client_socket.send(line)
                        current_size += len(line)
                        client.current_progress = (current_size / size)

        client.condition_send.clear()


def receiver_thread(client):
    while True:
        if client.is_finished:
            break

        received_data = client.client_socket.recv(BUFFER_SIZE)

        try:
            decoded_data = received_data.decode()
            if type_of_message(decoded_data) == "info":  # required for sending file
                if content_of_message(decoded_data) == "busy":
                    client.is_receiver_client_busy = True
                    client.condition_busy.set()
                elif content_of_message(decoded_data) == "not_busy":
                    client.is_receiver_client_busy = False
                    client.condition_busy.set()
                elif content_of_message(decoded_data) == "wrong_key":
                    client.is_receiver_client_busy = True
                    client.condition_busy.set()
                    client.wrong_key_trigger()

            elif type_of_message(decoded_data) == "size":  # required for receiving file
                client.size_of_file = int(content_of_message(decoded_data))
            elif type_of_message(decoded_data) == "name":  # required for receiving file
                client.name_of_file = str(content_of_message(decoded_data))
                client.file_descriptor = open(client.name_of_file, "wb")
                current_file_size = 0
                client.download_current_progress = 0
                client.downloading_trigger(client.name_of_file)
                while current_file_size != client.size_of_file:
                    received_data = client.client_socket.recv(BUFFER_SIZE)
                    try:
                        decoded_data = received_data.decode()
                        if type_of_message(decoded_data) == "info" and content_of_message(
                                decoded_data) == "interrupted":
                            client.recv_interrupted = True
                            break
                    except (UnicodeDecodeError, AttributeError):
                        pass

                    client.file_descriptor.write(received_data)
                    current_file_size += len(received_data)

                client.file_descriptor.close()
                if client.recv_interrupted:
                    os.remove(client.name_of_file)
                client.download_trigger(client.name_of_file)
                if client.recv_interrupted:
                    client.recv_interrupted = False
        except (UnicodeDecodeError, AttributeError):
            pass


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
                data, server_addr = multicast_sock.recvfrom(16)
            except socket.timeout:
                print('timed out, no more responses')
                break
            else:
                print(f'received server data: {data} from {server_addr}')
                return server_addr[0]     # returns real server ip
                # return data  # returns data sent from server -- here localhost ip

    finally:
        print('closing socket')
        multicast_sock.close()


class Client:
    def __init__(self, ip_address, port, download_trigger, downloading_trigger, wrong_key_trigger):
        self.ip_address = ip_address
        self.download_trigger = download_trigger
        self.downloading_trigger = downloading_trigger
        self.wrong_key_trigger = wrong_key_trigger
        self.port = port
        self.client_socket = None
        self.thread_pool = None
        self.file_path = None
        self.condition_send = threading.Event()
        self.condition_busy = threading.Event()
        self.is_finished = False
        self.is_ready_to_receive = False
        self.client_receiver_id = None
        self.is_receiver_client_busy = False
        self.client_id = None
        self.size_of_file = None
        self.name_of_file = None
        self.file_descriptor = None
        self.current_progress = 0
        self.download_current_progress = 0
        self.sending_interrupted = False
        self.recv_interrupted = False

    def initiate_connection(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_SCTP)
        self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.client_socket.connect((self.ip_address, self.port))
        self.client_id = self.client_socket.recv(BUFFER_SIZE).decode('utf-8')
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(2, thread_name_prefix="Client module")
        self.thread_pool.submit(sender_thread, self)
        self.thread_pool.submit(receiver_thread, self)

    def send_file(self, file_path, client_receiver_id):  # should be locked to end of communication
        self.current_progress = 0
        self.file_path = file_path
        self.client_receiver_id = client_receiver_id
        self.condition_send.set()

    def close_connection(self):
        self.is_finished = True
        self.client_receiver_id = None
        self.condition_send.set()
        self.client_socket.send("end:".encode('utf-8'))
        self.client_socket.shutdown(socket.SHUT_RDWR)
        self.thread_pool.shutdown(False)
