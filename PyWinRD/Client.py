from PyWinRD.Props import OUT_START, ERR_START, IN_START, SESSION_END, MESSAGE_END, SOCKET_DELAY, recv_all
from time import sleep
import socket
import sys
import os


class WinRDClient:

    def __init__(self, host='localhost', port=2345):
        self.host = host
        self.port = port

        self.address_family = socket.AF_INET
        self.protocol = socket.SOCK_STREAM

    def debug(self, path):
        soc = socket.socket(self.address_family, self.protocol)
        soc.connect((self.host, self.port))

        with open(path, 'rb') as f:
            soc.send(b''.join([bytes(os.path.basename(path), 'utf-8'), MESSAGE_END]))
            sleep(SOCKET_DELAY)

            soc.send(b''.join(f.readlines() + [MESSAGE_END]))

        while True:
            messages = recv_all(soc)

            for m in messages:

                if m.startswith(OUT_START):
                    m = m[len(OUT_START):]
                    sys.stdout.write(m.decode('utf-8'))

                elif m.startswith(ERR_START):
                    m = m[len(ERR_START):]
                    sys.stderr.write(m.decode('utf-8'))

                elif m == IN_START:
                    soc.send(b''.join([bytes(input(), 'utf-8'), MESSAGE_END]))

                elif m == SESSION_END:
                    soc.close()
                    break

            else:
                continue

            break
