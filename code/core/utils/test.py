import socket
from time import sleep

from core.config import shared as config


def test_tcp_stream(host: str, port: int, timeout: int = 5, out_error: bool = False) -> (bool, tuple):
    tcp_stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_stream.settimeout(timeout)

    try:
        tcp_stream.connect((host, port))
        tcp_stream.shutdown(socket.SHUT_RDWR)

    except (socket.timeout, socket.error, ConnectionError, ConnectionRefusedError, ConnectionResetError, ConnectionAbortedError) as error:
        pass

    sleep(0.2)
    tcp_stream.close()

    try:
        if error not in config.NONE_RESULTS:
            if out_error:
                return False, error

            return False

    except UnboundLocalError:  # setting 'error' to None initially doesn't seem to work for some reason (?)
        if out_error:
            return True, None

        return True
