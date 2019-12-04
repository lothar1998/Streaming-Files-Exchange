import logging
import concurrent.futures
import socket
import random

MAX_CLIENT_LISTEN = 10
MAX_CLIENT_LOGGED = 256000

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
c_handler = logging.FileHandler("log.log")
c_handler.setLevel(logging.INFO)
c_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
logger.addHandler(c_handler)


def receiver_module_execute(client_socket, client_address, client_id, thread_pool):
    pass
    logger.info("closing receiver module for client: %s", client_id)


def sender_module_execute(client_socket, client_address, client_id, thread_pool):
    pass
    logger.info("closing sender module for client: %s", client_id)


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
        logger.info("Server main thread has been started")
        main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        main_socket.bind((socket.gethostbyname(socket.gethostname()), self.server_port))
        main_socket.listen(MAX_CLIENT_LISTEN)
        logger.info("Server listen at port: %s", self.server_port)

        while True:
            (client_socket, client_address) = main_socket.accept()
            logger.info("connection accepted from: %s , port: %s", client_address[0], client_address[1])
            client_id = self.random_client_id()
            logger.info("assigned client_id: %s", client_id)
            self.thread_pool_executors_list[client_id] = concurrent.futures.ThreadPoolExecutor(2)
            client_executor = self.thread_pool_executors_list.get(client_id)
            logger.info("creating modules for client: %s", client_id)
            client_executor.submit(receiver_module_execute, client_socket, client_address, client_id, self.thread_pool_executors_list)
            client_executor.submit(sender_module_execute, client_socket, client_address, client_id, self.thread_pool_executors_list)


if __name__ == "__main__":
    server_module = Server(6969)
    server_module.start()
