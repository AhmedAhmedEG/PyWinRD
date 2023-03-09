import sys

OUT_START = b'SFO\00'
ERR_START = b'SOE\00'
IN_START = b'SOI\00'

MESSAGE_END = b'ME\00'
SESSION_END = b'SE\00'

SOCKET_DELAY = 0.005

STD_OUT = sys.stdout
STD_ERR = sys.stderr
STD_IN = sys.stdin


def recv_all(soc):
    data = b''
    while True:
        message = soc.recv(10 * 1024)
        data = b''.join([data, message])

        if data.endswith(MESSAGE_END):
            data = data.split(MESSAGE_END)
            data.pop()
            break

        elif not data:
            raise ConnectionLost

    return data


class ConnectionLost(Exception):
    pass
