import select

OUT_START = b'SFO\00'
ERR_START = b'SOE\00'

PORTION_END = b'PE\00'
MESSAGE_END = b'ME\00'

OPERATION_START = b'SS\00'
OPERATION_END = b'SE\00'

SOCKET_DELAY = 0.005


def recv_all(soc):
    data = b''

    while True:
        ready = select.select([soc], [], [], 1)[0]

        if ready:
            message = soc.recv(10 * 1024)
            data = b''.join([data, message])

            if data.endswith(MESSAGE_END):
                data = data.split(MESSAGE_END)
                data.pop()
                break

            elif not data:
                raise ConnectionResetError

    return data
