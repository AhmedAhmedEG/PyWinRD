from PyWinRD.Props import ERR_START, OUT_START, MESSAGE_END, SOCKET_DELAY, recv_all, OPERATION_END, OPERATION_START, PORTION_END
from subprocess import Popen, PIPE
from datetime import datetime
from threading import Thread
from pathlib import Path
from time import sleep
import traceback
import shutil
import socket
import sys

newline_used = True


class RemoteExecuter:

    def __init__(self, soc):
        self.soc = soc
        self.p = None
        self.exception = None

    def socket_stdout(self, s):
        global newline_used

        if s[-1] == '\n':
            newline_used = True

        else:
            newline_used = False

        sys.stdout.write(s)

        self.soc.sendall(b''.join([OUT_START, bytes(s, 'utf-8'), MESSAGE_END]))
        sleep(SOCKET_DELAY)

    def socket_stderr(self, s):
        global newline_used

        if s[-1] == '\n':
            newline_used = True

        else:
            newline_used = False

        sys.stderr.write(s)

        self.soc.sendall(b''.join([ERR_START, bytes(str(s), 'utf-8'), MESSAGE_END]))
        sleep(SOCKET_DELAY)

    def socket_stdin(self, s):
        sys.stdout.write(s.decode("utf-8"))

        self.p.stdin.write(s)
        self.p.stdin.flush()

    def stdout_listener(self):

        while self.p.poll() is None:
            o = self.p.stdout.read1().decode('utf-8')

            if o:
                self.socket_stdout(o)

    def stderr_listener(self):

        while self.p.poll() is None:
            e = self.p.stderr.read1().decode('utf-8')

            if e:
                self.socket_stderr(e)

    def stdin_listener(self):

        while self.p.poll() is None:

            try:
                messages = recv_all(self.soc)
                if messages[0] == OPERATION_START:
                    break

                for m in messages:
                    self.socket_stdin(m)

            except ConnectionResetError:
                self.exception = ConnectionResetError
                self.p.kill()
                break

    def process_listener(self, p: Popen, ol: Thread, el: Thread):

        while (p.poll() is None) or ol.is_alive() or el.is_alive():
            sleep(0.2)

        self.soc.sendall(b''.join([OPERATION_END, MESSAGE_END]))

    def execute(self, command):
        self.p = Popen(command.split(' '), stdout=PIPE, stderr=PIPE, stdin=PIPE)

        ol = Thread(target=self.stdout_listener, daemon=True)
        ol.start()

        el = Thread(target=self.stderr_listener, daemon=True)
        el.start()

        il = Thread(target=self.stdin_listener, daemon=True)
        il.start()

        while self.p.poll() is None:
            sleep(0.2)

        self.soc.sendall(b''.join([OPERATION_END, MESSAGE_END]))

        ol.join()
        el.join()
        il.join()


class WinRDServer:

    def __init__(self, host='', port=2345, password=''):
        self.host = host
        self.port = port
        self.password = password

        self.address_family = socket.AF_INET
        self.protocol = socket.SOCK_STREAM

        self.soc = socket.socket(self.address_family, self.protocol)
        self.soc.bind((self.host, self.port))

    def start(self):
        global newline_used

        self.soc.listen(1)
        while True:
            client_soc, client_addr = self.soc.accept()
            client_soc.setblocking(False)

            password = recv_all(client_soc)[0].decode('utf-8')
            if password != self.password:
                client_soc.sendall(b''.join([b'0', MESSAGE_END]))
                continue

            else:
                client_soc.sendall(b''.join([b'1', MESSAGE_END]))

            if not newline_used:
                sys.stderr.write('\n\n')
                newline_used = True
            sys.stderr.write(f'{datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")} {client_addr[0]} Connected.\n')

            remote_executer = RemoteExecuter(client_soc)
            Path('Temp').mkdir(exist_ok=True)

            while True:

                try:
                    info = recv_all(client_soc)[0].split(PORTION_END)
                    operation, data = info[0].decode('utf-8'), info[1:]

                    if operation == 'Deploy':
                        path = 'Temp' / Path(data[0].decode('utf-8'))

                        if not newline_used:
                            sys.stderr.write('\n')
                            newline_used = True
                        sys.stderr.write(f'{datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")} {client_addr[0]} Is Deploying "{path}".\n')

                        path.parent.mkdir(parents=True, exist_ok=True)
                        with open(path, 'wb') as f:
                            f.write(data[1])

                        client_soc.sendall(b''.join([OPERATION_END, MESSAGE_END]))
                        continue

                    elif operation == 'Terminal':
                        command = data[0].decode('utf-8')

                        if not newline_used:
                            sys.stderr.write('\n')
                            newline_used = True
                        sys.stderr.write(f'{datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")} {client_addr[0]} Is Executing "{command}".\n')

                        remote_executer.execute(command)

                    elif operation == 'Debug':
                        filename = data[0].decode('utf-8')

                        if not newline_used:
                            sys.stderr.write('\n')
                            newline_used = True
                        sys.stderr.write(f'{datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")} {client_addr[0]} Is Debugging "{filename}".\n')

                        path = 'Temp' / Path(filename)
                        with open(path, 'wb') as f:
                            f.write(data[1])

                        remote_executer.execute(f'python {path}')
                        if remote_executer.exception:
                            raise remote_executer.exception

                    else:
                        continue

                except ConnectionResetError:
                    break

                except Exception: # noqa
                    traceback.print_exc()

            if not newline_used:
                sys.stderr.write('\n')
                newline_used = True
            sys.stderr.write(f'{datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")} {client_addr[0]} Disconnected.\n\n')

            shutil.rmtree('Temp', ignore_errors=True)