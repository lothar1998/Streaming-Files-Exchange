import logging
import concurrent.futures
import socket
import random
import threading
from ServerReceiverModule import ServerReceiverModule
from ServerSendModule import ServerSendModule
import queue
import time

MAX_CLIENT_LISTEN = 10
MAX_CLIENT_LOGGED = 256000

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler("log.log")
handler.setLevel(logging.INFO)
handler_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(handler_format)
logger.addHandler(handler)


def receiver_module_execute(client_socket, client_address, client_id, server):
    logger.info("reveiver: " + threading.current_thread().getName())

    srm = ServerReceiverModule(client_id, server.client_dictionary, client_socket)
    srm.receive_data()
    logger.info("closing receiver module for client: %s", client_id)
    server.client_dictionary[client_id][0].shutdown(False)


def sender_module_execute(client_socket, client_address, client_id, server):
    logger.info("sender: " + threading.current_thread().getName())

    ssm = ServerSendModule(client_id, server.client_dictionary, client_socket)
    ssm.send_data()
    logger.info("closing sender module for client: %s", client_id)
    server.client_dictionary[client_id][0].shutdown(False)


class Server:
    def __init__(self, server_port):
        self.server_port = server_port
        self.client_dictionary = dict()

    def random_client_id(self):
        while True:
            x = random.randint(1, MAX_CLIENT_LOGGED)
            if x not in self.client_dictionary:
                return x

    def start(self):
        logger.info("Server main thread has been started")
        main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_SCTP)
        main_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        main_socket.bind(("127.0.0.1", self.server_port))
        main_socket.listen(MAX_CLIENT_LISTEN)
        logger.info("Server listen at port: %s", self.server_port)

        while True:
            (client_socket, client_address) = main_socket.accept()
            logger.info("connection accepted from: %s , port: %s", client_address[0], client_address[1])
            client_id = self.random_client_id()
            client_socket.send(str(client_id).encode('utf-8'))
            logger.info("assigned client_id: %s", client_id)
            self.client_dictionary[client_id] = [concurrent.futures.ThreadPoolExecutor(2), False, queue.Queue()]
            client_executor = self.client_dictionary.get(client_id)[0]
            logger.info("creating modules for client: %s", client_id)
            client_executor.submit(receiver_module_execute, client_socket, client_address, client_id, self)
            client_executor.submit(sender_module_execute, client_socket, client_address, client_id, self)


if __name__ == "__main__":
    server_module = Server(6969)
    server_module.start()
