import socket
from time import sleep

from core.config.shared import NONE_RESULTS


def test_tcp_stream(host: str, port: int, timeout: int = 5, out_error: bool = False) -> (bool, tuple):
    error = None
    tcp_stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_stream.settimeout(timeout)

    try:
        tcp_stream.connect((host, port))
        tcp_stream.shutdown(socket.SHUT_RDWR)

    except (socket.timeout, socket.error, ConnectionError, ConnectionRefusedError, ConnectionResetError, ConnectionAbortedError) as error:
        pass

    sleep(0.2)
    tcp_stream.close()

    if out_error:
        if error not in NONE_RESULTS:
            return False, error
        else:
            return True, None

    else:
        if error not in NONE_RESULTS:
            return False
        else:
            return True

