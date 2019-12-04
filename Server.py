import logging
import time
import threading
import concurrent.futures
import socket
import random

MAX_CLIENT_LISTEN = 10
MAX_CLIENT_LOGGED = 256000


def receiver_module_execute(client_socket, client_address, client_id, thread_pool):
    print("receiver")
    print(client_socket)
    print(client_address)
    print(client_id)
    print(thread_pool)


def sender_module_execute(client_socket, client_address, client_id, thread_pool):
    print("sender")
    print(client_socket)
    print(client_address)
    print(client_id)
    print(thread_pool)


class Server:
    def __init__(self, server_port):
        self.server_port = server_port
        self.thread_pool_executors_list = dict()

    def random_client_id(self):
        while True:
            x = random.randint(1, MAX_CLIENT_LOGGED)
            if x not in self.thread_pool_executors_list:
                return x

    def start(self):
        logging.log()
        main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        main_socket.bind((socket.gethostbyname(socket.gethostname()), self.server_port))
        main_socket.listen(MAX_CLIENT_LISTEN)

        while True:
            (client_socket, client_address) = main_socket.accept()
            client_id = self.random_client_id()
            self.thread_pool_executors_list[client_id] = concurrent.futures.ThreadPoolExecutor(2)
            client_executor = self.thread_pool_executors_list.get(client_id)
            client_executor.submit(receiver_module_execute, client_socket, client_address, client_id, self.thread_pool_executors_list)
            client_executor.submit(sender_module_execute, client_socket, client_address, client_id, self.thread_pool_executors_list)


if __name__ == "__main__":
    server_module = Server(6969)
    server_module.start()
