import logging
import concurrent.futures
import socket
import random
import threading
from ServerReceiverModule import ServerReceiverModule
from ServerSendModule import ServerSendModule
import queue
import struct
import daemon
import os

MAX_CLIENT_LISTEN = 10
MAX_CLIENT_LOGGED = 256000
MULTICAST_GROUP = '224.1.1.1'

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler("log.log")
handler.setLevel(logging.INFO)
handler_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(handler_format)
logger.addHandler(handler)


def create_daemon():
    logger.info("Creating daemon process")
    server_module = Server(6969)
    server_module.start()


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


def multicast_thread_cleanup(multicast_thread):
    logger.info("Closing multicast handler thread")
    multicast_thread.shutdown(False)


def multicast_handler(server):
    logger.info("Starting multicast thread")
    multicast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    multicast_socket.bind(('', server.server_port))

    group = socket.inet_aton(MULTICAST_GROUP)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    while True:
        _, address = multicast_socket.recvfrom(1024)

        # server_ip = server.server_ip
        server_ip = '127.0.0.1'
        multicast_socket.sendto(bytes(server_ip, 'utf-8'), address)
    # TODO: shutdown thread


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
        # try:
        logger.info("Server main thread has been started")
        # TODO: IPPROTO_SCTP
        main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        main_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        main_socket.bind(("127.0.0.1", self.server_port))

        multicast_thread = concurrent.futures.ThreadPoolExecutor(1, thread_name_prefix="multicast")
        multicast_thread.submit(multicast_handler, self)

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
        # except(KeyboardInterrupt, SystemExit):
        #     multicast_thread_cleanup(multicast_thread)


if __name__ == "__main__":
    logger.info("Running server")
    uid = os.getuid()
    if uid == 0:
        # means that is root, so change it to 'normal user'
        uid = 501

    gid = os.getgid()
    if gid == 0:
        # same for group
        gid = 20

    if hasattr(os, "devnull"):
        REDIRECT_TO = os.devnull
    else:
        REDIRECT_TO = "/dev/null"
    """
    DaemonContext:
        - detached=True,
        - working_directory='/'
        - umask=0
        - files_preserve=None # closes all opened descriptors
    """
    with daemon.DaemonContext(uid=uid, gid=gid):
        create_daemon()
