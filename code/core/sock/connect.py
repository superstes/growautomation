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
from core.utils.debug import log
from core.sock.translate import Route


class Interact:
    def __init__(self, link, server: bool = False):
        self.LINK = link
        self.BANNER = socket_config.SOCKET_BANNER_CORE
        self.HEAD = socket_config.PACKAGE_START.encode('utf-8')
        self.TAIL = socket_config.PACKAGE_STOP.encode('utf-8')
        self.SIZE = socket_config.PACKAGE_SIZE
        self.SERVER = server
        self.SHUFFLE = socket_config.SHUFFLE
        self.PATH_SEP = socket_config.PACKAGE_PATH_SEPARATOR
        if self.SERVER:
            self.LOG_PREFIX = 'Server - '
        else:
            self.LOG_PREFIX = 'Client - '

        if self.SHUFFLE:
            log(f'{self.LOG_PREFIX}Shuffling transferred data', level=7)

    def send(self, data: str) -> (bool, dict):
        try:
            data_enc = data.encode('utf-8')

            if self.SHUFFLE:
                log(f'{self.LOG_PREFIX}Sending data: {data_enc}', level=9)
                data_send = self._shuffle(data_enc)

            else:
                data_send = data_enc

            data_packed = str(len(data_send)).encode('utf-8')
            data_packed += self.HEAD
            data_packed += data_send
            data_packed += self.TAIL

            log(f'{self.LOG_PREFIX}Sending packet: {data_packed}', level=9)
            self.LINK.sendall(data_packed)

            if not self.SERVER:
                response = self.receive()
                if response is not None:
                    return response

            return True

        except Exception as error:
            log(f"{self.LOG_PREFIX}Got error while sending data: '{error}'", level=3)
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
                    log(f'{self.LOG_PREFIX}Received no data!', level=9)

                    if time() > start_time + socket_config.RECV_TIMEOUT:
                        log(f'{self.LOG_PREFIX}Receive timeout!', level=5)
                        return False

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

            log(f'{self.LOG_PREFIX}Received data: {data_recv}', level=8)

            if self.SHUFFLE:
                # remove un-shuffled head and tail and get the plaintext data
                data = self.HEAD + self._shuffle(data_recv[len(self.HEAD):-len(self.TAIL)]) + self.TAIL
                log(f'{self.LOG_PREFIX}Un-shuffled data: {data}', level=9)

            else:
                data = data_recv

            return self._validate(data.decode('utf-8'))

        except Exception as error:
            log(f"{self.LOG_PREFIX}Got error while receiving data: '{error}'", level=3)
            return False

    def _validate(self, data: str) -> (dict, None):
        head_str = self.HEAD.decode('utf-8')
        tail_str = self.TAIL.decode('utf-8')

        if data.startswith(head_str) and data.endswith(tail_str):
            _ = data[len(head_str):-len(tail_str)].split(self.PATH_SEP)
            try:
                return {'path': _[0], 'data': _[1]}

            except IndexError:
                log(f"{self.LOG_PREFIX}Wasn't able to parse received data!", level=3)

        else:
            log(f'{self.LOG_PREFIX}Received invalid data!', level=3)

        return None

    @staticmethod
    def _shuffle(data: (bytes, str)) -> bytes:
        if type(data) == str:
            data = data.encode('utf-8')

        return bytes(
            [a ^ b for (a, b) in zip(data, cycle(socket_config.SHUFFLE_DATA))]
        )


class Client:
    def __init__(self, path: str, target: str = '127.0.0.1', port: int = socket_config.SOCKET_PORT):
        self.PATH = path if path.startswith('ga.') else f'{socket_config.PATH_WEB}.{path}'
        self.LINK = socket(family=AF_INET, type=SOCK_STREAM)
        self.TARGET = target
        self.PORT = port
        self.PATH_SEP = socket_config.PACKAGE_PATH_SEPARATOR
        self.LOG_PREFIX = 'Client - '
        self.connected = False
        self.LINK.settimeout(socket_config.RECV_TIMEOUT)

    def get(self) -> (str, None):
        if self.connected or self._init():
            return Interact(link=self.LINK).receive()

    def post(self, data: str) -> (bool, dict):
        if self.connected or self._init():
            return Interact(link=self.LINK).send(data=f'{self.PATH}{self.PATH_SEP}{data}')

    def _init(self):
        try:
            self.LINK.connect((self.TARGET, self.PORT))
            self.connected = True
            return True

        except socket_error as error:
            log(f"{self.LOG_PREFIX}Got error connecting to server '{self.TARGET}': {error}", level=3)
            return False

    def __del__(self):
        self.LINK.close()


def server_thread(srv, connection):
    # handles client connections; did not work as method of 'Server'..
    try:
        start_time = time()
        srv.CLIENT_THREADS += 1
        log(f'{srv.LOG_PREFIX}Entered Client-Thread #{srv.CLIENT_THREADS}', level=6)
        data = Interact(link=connection, server=True).receive()
        log(f"{srv.LOG_PREFIX}Received data: '{data}'", level=6)

        if data is None:
            log(f'{srv.LOG_PREFIX}Unable to get route', level=6)

        else:
            # parsing command and executing api
            result, status = Route(parsed=data).go()
            result_str = 'success' if result else 'failed'
            Interact(link=connection, server=True).send(data=f'result:{result_str},status:{status}')

        log(f"{srv.LOG_PREFIX}Processed client connection to '{connection.raddr}' in {time()-start_time} secs", level=6)
        srv.CLIENT_THREADS -= 1
        return data

    except:
        exc_type, exc_obj, _ = sys_exc_info()
        log(f"Client connection '{connection.raddr}' failed with error: \"{exc_type} - {exc_obj}\"", level=1)
        log(f"{format_exc()}"[:config.LOG_MAX_TRACEBACK_LENGTH], level=4)


class Server:
    BIND_RETRY_SLEEP = 5
    BIND_RETRY_MAX_COUNT = 60

    def __init__(self):
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

    def run(self):
        retry = 0

        while retry < self.BIND_RETRY_MAX_COUNT:
            try:
                retry += 1
                self.SERVER.bind((self.ADDRESS, self.PORT))
                log(f'{self.LOG_PREFIX}Successfully bound {self.NAME} on {self.ADDRESS}:{self.PORT}', level=6)
                break

            except OSError:
                # when the server was killed; it will need some time until tcp releases the socket
                log(f'{self.LOG_PREFIX}Port {self.PORT} is not free; retrying..', level=5)
                sleep(self.BIND_RETRY_SLEEP)

        try:
            self.SERVER.listen(self.CLIENT_MAX_CONCURRENT)

            while True:
                connection, address = self.SERVER.accept()
                connection.settimeout(socket_config.RECV_TIMEOUT)
                log(f"{self.LOG_PREFIX}Client {address[0]}:{address[1]} connected to the {self.NAME}!", level=6)
                start_new_thread(server_thread, (self, connection))

        except (Exception, KeyboardInterrupt) as error:
            log(f"{self.LOG_PREFIX}{self.NAME} got error: '{error}'", level=5)

    def __del__(self):
        self.SERVER.close()

