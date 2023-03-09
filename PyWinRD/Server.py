from PyWinRD.Props import IN_START, ERR_START, OUT_START, STD_OUT, STD_ERR, SESSION_END, MESSAGE_END, SOCKET_DELAY, ConnectionLost, recv_all
from datetime import datetime
from time import sleep
import traceback
import socket
import sys

newline_used = True


class SocketOut:

    def __init__(self, soc):
        super().__init__()
        self.soc = soc

    def write(self, s):
        global newline_used

        if s[-1] == '\n':
            newline_used = True

        else:
            newline_used = False

        STD_OUT.write(s)

        sleep(SOCKET_DELAY)
        self.soc.send(b''.join([OUT_START, bytes(s, 'utf-8'), MESSAGE_END]))

    def flush(self):
        pass


class SocketErr:

    def __init__(self, soc):
        super().__init__()
        self.soc = soc

    def write(self, s):
        global newline_used

        if s[-1] == '\n':
            newline_used = True

        else:
            newline_used = False

        STD_ERR.write(s)

        sleep(SOCKET_DELAY)
        self.soc.send(b''.join([ERR_START, bytes(str(s), 'utf-8'), MESSAGE_END]))

    def flush(self, s=''):
        pass


class SocketIn:

    def __init__(self, soc):
        super().__init__()
        self.soc = soc

    def readline(self):
        self.soc.send(b''.join([IN_START, MESSAGE_END]))
        message = recv_all(self.soc)[0].decode('utf-8')

        STD_OUT.write(f'{message}\n')

        return message


class WinRDServer:

    def __init__(self, host='', port=2345):
        self.host = host
        self.port = port

        self.address_family = socket.AF_INET
        self.protocol = socket.SOCK_STREAM

    def start(self):
        global newline_used

        while True:
            soc = socket.socket(self.address_family, self.protocol)
            soc.bind((self.host, self.port))
            soc.listen()

            client_soc, client_addr = soc.accept()

            filename = recv_all(client_soc)[0].decode('utf-8')
            if not newline_used:
                STD_ERR.write('\n')
            STD_ERR.write(f'{datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")} {client_addr[0]} Is Debugging {filename}.\n')

            sys.stdout = SocketOut(client_soc)
            sys.stderr = SocketErr(client_soc)
            sys.stdin = SocketIn(client_soc)

            data = recv_all(client_soc)[0]
            try:
                exec(data)

            except ConnectionLost:

                if not newline_used:
                    STD_ERR.write('\n')
                STD_ERR.write(f'{datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")} {client_addr[0]} Connection Lost.\n')

                soc.close()
                continue

            except Exception:
                traceback.print_exc()

            if not newline_used:
                STD_ERR.write('\n')
            STD_ERR.write(f'{datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")} {client_addr[0]} Finished Debugging {filename}.\n')

            client_soc.send(b''.join([SESSION_END, MESSAGE_END]))
            soc.close()