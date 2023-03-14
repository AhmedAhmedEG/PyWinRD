from PyWinRD.Props import OUT_START, ERR_START, MESSAGE_END, SOCKET_DELAY, recv_all, OPERATION_END, OPERATION_START, PORTION_END
from threading import Thread
from pathlib import Path
from time import sleep
import socket
import sys


class WinRDClient:

    def __init__(self, host='localhost', port=2345, password=''):
        self.host = host
        self.port = port
        self.password = password
        self.soc = None

        self.address_family = socket.AF_INET
        self.protocol = socket.SOCK_STREAM

        Thread(target=self.stdin_listener, daemon=True).start()

    def stdin_listener(self):

        while True:
            i = sys.stdin.readline()

            if self.soc is not None:
                self.soc.send(b''.join([bytes(i, 'utf-8'), MESSAGE_END]))

    def terminal(self, command):

        if type(command) == list:

            for c in command:
                self.communicate('Terminal', bytes(c, 'utf-8'))

        else:
            self.communicate('Terminal', bytes(command, 'utf-8'))

    def deploy(self, path):
        path = Path(path)
        files = []

        if path.is_file():

            with open(path, 'rb') as f:
                lines = b''.join(f.readlines())

            files.append([str(path), lines])

        elif path.is_dir():

            for p in path.rglob('*'):

                if p.is_file():

                    with open(p, 'rb') as f:
                        lines = b''.join(f.readlines())

                    files.append([str(p), lines])

        for f in files:
            self.communicate('Deploy', b''.join([bytes(f[0], 'utf-8'), PORTION_END, f[1]]))

    def debug(self, path):
        path = Path(path)

        with open(path, 'rb') as f:
            lines = b''.join(f.readlines())

        self.communicate('Debug', b''.join([bytes(path.name, 'utf-8'), PORTION_END, lines]))

    def connect(self):
        self.soc = socket.socket(self.address_family, self.protocol)
        self.soc.connect((self.host, self.port))

        self.soc.send(b''.join([bytes(self.password, 'utf-8'), MESSAGE_END]))
        sleep(SOCKET_DELAY)

        response = recv_all(self.soc)[0]
        if response == b'0':
            print('Password is wrong.')
            return

    def disconnect(self):
        self.soc.close()
        self.soc = None

    def communicate(self, name, data):
        self.soc.sendall(b''.join([OPERATION_START, MESSAGE_END]))
        sleep(SOCKET_DELAY)

        name = bytes(name, 'utf-8')
        self.soc.sendall(b''.join([name, PORTION_END, data, MESSAGE_END]))
        sleep(SOCKET_DELAY)

        while True:
            messages = recv_all(self.soc)

            for m in messages:

                if m.startswith(OUT_START):
                    m = m[len(OUT_START):]
                    sys.stdout.write(m.decode('utf-8'))

                elif m.startswith(ERR_START):
                    m = m[len(ERR_START):]
                    sys.stderr.write(m.decode('utf-8'))

                elif m.startswith(OPERATION_END):
                    break

            else:
                continue

            break
