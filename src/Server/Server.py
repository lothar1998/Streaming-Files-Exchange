import logging
import concurrent.futures
import socket
import random
import threading
from src.Server.ServerReceiverModule import ServerReceiverModule
from src.Server.ServerSendModule import ServerSendModule
import queue
import struct
import daemon
import os
import sys
import signal

MAX_CLIENT_LISTEN = 10
MAX_CLIENT_LOGGED = 256000
MULTICAST_GROUP = '224.1.1.1'
MULTICAST_THREAD = None


def get_logger_file(name, file_path, log_level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    handler = logging.FileHandler(file_path)
    handler.setLevel(logging.INFO)
    handler_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(handler_format)
    logger.addHandler(handler)
    return logger


class LoggerWrapper:
    def __init__(self, logger):
        self.logger = logger

    def write(self, msg):
        msg = msg.rstrip()
        if msg:  # log only if msg not empty
            for line in msg.split('\n'):
                self.logger.critical(line)  # log independent of log level

    def flush(self):
        for handler in self.logger.handlers:
            handler.flush()

    def close(self):
        for handler in self.logger.handlers:
            handler.close()


def open_logger_files(loggers):
    open_files = []
    for logger in loggers:
        for handler in logger.handlers:
            if hasattr(handler, 'stream') and hasattr(handler.stream, 'fileno'):
                open_files.append(handler.stream)
    return open_files


class ServerDaemonContext(daemon.DaemonContext):
    def __init__(self, chroot_directory=None, working_directory='/', umask=0, prevent_core=True,
                 detach_process=None, files_preserve=[], loggers_preserve=[], pidfile=None, stdout_logger=None,
                 stderr_logger=None, signal_map=None):

        self.stdout_logger = stdout_logger
        self.stderr_logger = stderr_logger
        self.loggers_preserve = loggers_preserve

        if hasattr(os, "devnull"):
            redirect = os.devnull
        else:
            redirect = "/dev/null"

        devnull_in = open(redirect, 'r+')
        devnull_out = open(redirect, 'w+')
        files_preserve.extend([devnull_in, devnull_out])

        uid = os.getuid()
        if uid == 0:
            # means that is root, so change it to 'normal user'
            uid = 501

        gid = os.getgid()
        if gid == 0:
            # same for group
            gid = 20

        daemon.DaemonContext.__init__(self,
                                      chroot_directory=chroot_directory,
                                      working_directory=working_directory,
                                      umask=umask,
                                      uid=uid,
                                      gid=gid,
                                      prevent_core=prevent_core,
                                      detach_process=detach_process,
                                      files_preserve=files_preserve,
                                      pidfile=pidfile,
                                      stdin=devnull_in,
                                      stdout=devnull_out,
                                      stderr=devnull_out,
                                      signal_map=signal_map)

    def _add_loggers(self):
        for logger in [self.stdout_logger, self.stderr_logger]:
            if logger:
                self.loggers_preserve.append(logger)
        logger_files = open_logger_files(self.loggers_preserve)
        self.files_preserve.extend(logger_files)

    def open(self):
        self._add_loggers()
        daemon.DaemonContext.open(self)
        if self.stdout_logger:
            logger_obj = LoggerWrapper(self.stdout_logger)
            sys.stdout = logger_obj
        if self.stderr_logger:
            logger_obj = LoggerWrapper(self.stderr_logger)
            sys.stderr = logger_obj


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


def server_cleanup(signum, stack):
    global MULTICAST_THREAD
    logger.info(f"RECEIVED {signum} : Cleaning up")
    MULTICAST_THREAD.shutdown(False)
    sys.exit(0)


def multicast_handler(server):
    logger.info("Starting multicast thread")
    multicast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    multicast_socket.bind(('', server.server_port))

    group = socket.inet_aton(MULTICAST_GROUP)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    while True:
        _, address = multicast_socket.recvfrom(1024)

        server_msg = 'ACK'
        multicast_socket.sendto(bytes(server_msg, 'utf-8'), address)


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
        global MULTICAST_THREAD
        logger.info("Server main thread has been started")
        main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_SCTP)
        main_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        addr = s.getsockname()[0]
        s.close()

        main_socket.bind((addr, self.server_port))

        MULTICAST_THREAD = concurrent.futures.ThreadPoolExecutor(1)
        MULTICAST_THREAD.submit(multicast_handler, self)

        signal.signal(signal.SIGTERM, server_cleanup)
        signal.signal(signal.SIGINT, server_cleanup)

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
    logger = get_logger_file("basic_logger", "/var/log/stream_server.log")
    stdoutLogger = get_logger_file('stdout', '/var/log/stream_server_stdout.log')
    stderrLogger = get_logger_file('stderr', '/var/log/stream_server_stderr.log')

    context = ServerDaemonContext()
    context.loggers_preserve = [logger]
    context.stdout_logger = stdoutLogger
    context.stderr_logger = stderrLogger

    with context:
        logger.info("Running server")

        server_module = Server(6969)
        server_module.start()
