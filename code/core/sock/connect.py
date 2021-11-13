# provides socket server and client

from socket import socket, AF_INET, SOCK_STREAM
from socket import error as socket_error
from _thread import start_new_thread
from time import sleep, time
from itertools import cycle
from sys import exc_info as sys_exc_info
from traceback import format_exc

from core.config import socket as socket_config
from core.config import shared as config
from core.sock.translate import Route
from core.utils.debug import log


class Interact:
    def __init__(self, link, logger=log, server: bool = False, timeout: int = None):
        self.LINK = link
        self.LOG = logger
        self.BANNER = socket_config.SOCKET_BANNER_CORE
        self.HEAD = socket_config.PACKAGE_START.encode('utf-8')
        self.TAIL = socket_config.PACKAGE_STOP.encode('utf-8')
        self.SIZE = socket_config.PACKAGE_SIZE
        self.SERVER = server
        self.SHUFFLE = socket_config.SHUFFLE
        self.PATH_SEP = socket_config.PACKAGE_PATH_SEPARATOR
        self.TIMEOUT = timeout if timeout is not None else socket_config.RECV_TIMEOUT
        if self.SERVER:
            self.LOG_PREFIX = 'Server - '

        else:
            self.LOG_PREFIX = 'Client - '

        if self.SHUFFLE:
            self.LOG(f'{self.LOG_PREFIX}Shuffling data!', level=6)
            # self.LOG(f'{self.LOG_PREFIX}Shuffle config {config.SOCKET_SHUFFLE} {type(config.SOCKET_SHUFFLE)}, {config.SERVER.security} {type(config.SERVER.security)}!', level=6)

    def send(self, data: str) -> (bool, dict):
        try:
            data_enc = data.encode('utf-8')

            if self.SHUFFLE:
                self.LOG(f'{self.LOG_PREFIX}Sending data: {data_enc}', level=9)
                data_send = self._shuffle(data_enc)

            else:
                data_send = data_enc

            data_packed = str(len(data_send)).encode('utf-8')
            data_packed += self.HEAD
            data_packed += data_send
            data_packed += self.TAIL

            self.LOG(f'{self.LOG_PREFIX}Sending packet: {data_packed}', level=9)
            self.LINK.sendall(data_packed)

            if not self.SERVER:
                response = self.receive()

                if response is not None:
                    return response

                else:
                    self.LOG(f'{self.LOG_PREFIX}Got no response from request!', level=5)

            return None

        except Exception as error:
            self.LOG(f"{self.LOG_PREFIX}Got error while sending data: '{error}'", level=3)
            return False

    def receive(self) -> (dict, None):
        try:
            data_recv = bytearray()
            data_len = 1
            header = True
            start_time = time()

            while len(data_recv) < data_len:
                pending_data = data_len - len(data_recv)

                if header:
                    # if first
                    data_enc = self.LINK.recv(10)

                elif pending_data < self.SIZE:
                    # if last
                    data_enc = self.LINK.recv(pending_data)

                else:
                    data_enc = self.LINK.recv(self.SIZE)

                if not data_enc:
                    # if we did not receive anything
                    self.LOG(f'{self.LOG_PREFIX}Received no data!', level=9)

                    if time() > start_time + self.TIMEOUT:
                        self.LOG(f'{self.LOG_PREFIX}Receive timeout!', level=5)
                        return None

                    else:
                        sleep(socket_config.RECV_INTERVAL)

                elif header:
                    # if first package => get package length and remove header
                    head_counter, data_start = data_enc.split(self.HEAD)
                    data_enc = self.HEAD + data_start
                    data_len = int(head_counter)
                    data_len += len(self.HEAD) + len(self.TAIL)
                    data_recv.extend(data_enc)
                    header = False

                else:
                    data_recv.extend(data_enc)

            self.LOG(f'{self.LOG_PREFIX}Received data: {data_recv}', level=8)

            if self.SHUFFLE:
                # remove un-shuffled head and tail and get the plaintext data
                data = self.HEAD + self._shuffle(data_recv[len(self.HEAD):-len(self.TAIL)]) + self.TAIL
                self.LOG(f'{self.LOG_PREFIX}Un-shuffled data: {data}', level=9)

            else:
                data = data_recv

            return self._validate(data.decode('utf-8'))

        except Exception as error:
            self.LOG(f"{self.LOG_PREFIX}Got error while receiving data: '{error}'", level=3)
            return None

    def _validate(self, data: str) -> (dict, None):
        head_str = self.HEAD.decode('utf-8')
        tail_str = self.TAIL.decode('utf-8')

        if data == socket_config.NONE_RESULT:
            self.LOG(f'{self.LOG_PREFIX}Received empty result!', level=3)

        elif data.startswith(head_str) and data.endswith(tail_str):
            _ = data[len(head_str):-len(tail_str)].split(self.PATH_SEP)
            try:
                return {'path': _[0], 'data': _[1]}

            except IndexError:
                self.LOG(f"{self.LOG_PREFIX}Wasn't able to parse received data!", level=3)
                data_one_line = data.replace('\n', '\\n')
                self.LOG(f"{self.LOG_PREFIX}Data: \"{data_one_line}\"!", level=6)

        else:
            self.LOG(f'{self.LOG_PREFIX}Received invalid data!', level=3)

        return None

    @staticmethod
    def _shuffle(data: (bytes, str)) -> bytes:
        if type(data) == str:
            data = data.encode('utf-8')

        return bytes(
            [a ^ b for (a, b) in zip(data, cycle(socket_config.SHUFFLE_DATA))]
        )


class Client:
    def __init__(self, path: str, logger=log, target: str = '127.0.0.1', port: int = socket_config.SOCKET_PORT, timeout: int = None):
        self.PATH = path if path.startswith('ga.') else f'{socket_config.PATH_WEB}.{path}'
        self.LINK = socket(family=AF_INET, type=SOCK_STREAM)
        self.TARGET = target
        self.PORT = port
        self.PATH_SEP = socket_config.PACKAGE_PATH_SEPARATOR
        self.LOG_PREFIX = 'Client - '
        self.connected = False
        self.LINK.settimeout(socket_config.RECV_TIMEOUT)
        self.LOG = logger
        self.TIMEOUT = timeout

    def get(self) -> (str, None):
        if self.connected or self._init():
            return Interact(link=self.LINK, logger=self.LOG, timeout=self.TIMEOUT).receive()

    def post(self, data: str) -> (bool, dict):
        if self.connected or self._init():
            return Interact(link=self.LINK, logger=self.LOG, timeout=self.TIMEOUT).send(data=f'{self.PATH}{self.PATH_SEP}{data}')

    def _init(self):
        try:
            self.LINK.connect((self.TARGET, self.PORT))
            self.connected = True
            return True

        except socket_error as error:
            self.LOG(f"{self.LOG_PREFIX}Got error connecting to server '{self.TARGET}': {error}", level=3)
            return None

    def __del__(self):
        self.LINK.close()


def server_thread(srv, connection, client):
    # handles client connections; did not work as method of 'Server'..
    try:
        start_time = time()
        srv.CLIENT_THREADS += 1
        srv.LOG(f'{srv.LOG_PREFIX}Entered Client-Thread #{srv.CLIENT_THREADS}', level=6)
        data = Interact(link=connection, server=True, logger=srv.LOG).receive()
        srv.LOG(f"{srv.LOG_PREFIX}Received data: '{data}'", level=6)

        if data is None:
            srv.LOG(f'{srv.LOG_PREFIX}Unable to get route', level=6)
            Interact(
                link=connection,
                server=True,
                logger=srv.LOG
            ).send(data=socket_config.NONE_RESULT)  # return none-result to client so it does not wait for a response that will never come

        else:
            # parsing command and executing api
            result = Route(parsed=data).go()
            Interact(
                link=connection,
                server=True,
                logger=srv.LOG
            ).send(
                data=f"{data['path']}"
                     f"{socket_config.PACKAGE_PATH_SEPARATOR}"
                     f"{result}"
            )

        srv.LOG(f"{srv.LOG_PREFIX}Processed client connection to '{client}' in %.3f secs" % (time() - start_time), level=6)
        srv.CLIENT_THREADS -= 1
        return data

    except:
        srv.CLIENT_THREADS -= 1
        exc_type, exc_obj, _ = sys_exc_info()
        srv.LOG(f"Client connection '{client}' failed with error: \"{exc_type} - {exc_obj}\"", level=1)
        srv.LOG(f"{format_exc(limit=config.LOG_MAX_TRACEBACK_LENGTH)}", level=4)


class Server:
    BIND_RETRY_SLEEP = 5
    BIND_RETRY_MAX_COUNT = 60

    def __init__(self, logger=log):
        self.SERVER = socket(family=AF_INET, type=SOCK_STREAM)
        self.PORT = socket_config.SOCKET_PORT

        if socket_config.SOCKET_PUBLIC:
            self.ADDRESS = ''  # listen on all available addresses

        else:
            self.ADDRESS = '127.0.0.1'

        self.CLIENT_MAX_CONCURRENT = 5
        self.CLIENT_THREADS = 0
        self.PKG_SIZE = socket_config.PACKAGE_SIZE
        self.NAME = socket_config.SOCKET_SERVER_NAME
        self.LOG_PREFIX = 'Server - '
        self.LOG = logger

    def run(self):
        retry = 0

        while retry < self.BIND_RETRY_MAX_COUNT:
            try:
                retry += 1
                self.SERVER.bind((self.ADDRESS, self.PORT))
                self.LOG(f'{self.LOG_PREFIX}Successfully bound {self.NAME} on {self.ADDRESS}:{self.PORT}', level=6)
                break

            except OSError:
                # when the server was killed; it will need some time until tcp releases the socket
                self.LOG(f'{self.LOG_PREFIX}Port {self.PORT} is not free; retrying..', level=5)
                sleep(self.BIND_RETRY_SLEEP)

        try:
            self.SERVER.listen(self.CLIENT_MAX_CONCURRENT)

            while True:
                connection, address = self.SERVER.accept()
                client = f'{address[0]}:{address[1]}'
                connection.settimeout(socket_config.RECV_TIMEOUT)
                self.LOG(f"{self.LOG_PREFIX}Client {client} connected to the {self.NAME}!", level=6)
                start_new_thread(server_thread, (self, connection, client))

        except (Exception, KeyboardInterrupt) as error:
            self.LOG(f"{self.LOG_PREFIX}{self.NAME} got error: '{error}'", level=5)

    def __del__(self):
        self.SERVER.close()

