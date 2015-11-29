# server.py

import sys
import socket
import select
import traceback
import logging
from collections import deque

from dill import loads, dumps
import numpy as np

Instance = type(object())


class Handler(object):
    def __init__(self):
        self.data = deque()

    def enque(self, item):
        self.data.append(item)

    def work(self):
        if len(self.data) > 0:
            item = self.data.popleft()
            logging.info("De-que'd %s" % typeData(item))


def typeData(data):
    if isinstance(data, np.ndarray):
        dataStr = str(data.shape)
    else:
        dataStr = str(data).strip()
    return "%s: '%s'" % (type(data), dataStr)


def recv(sock, length=2 ** 13, unpickle=True):
    data = sock.recv(length)
    try:
        data = loads(data)
    except (KeyError, IndexError) as e:
        import warnings
        warnings.warn(str(e))
        return False, None
    sys.stdout.flush()
    logging.info("Got data: %s" % typeData(data))
    sys.stdout.flush()
    return True, data


SOCKET_LIST = []
def server(HOST='', PORT=9009):
    RECV_BUFFER = 2 ** 16
    def removeSocket(sock):
        if sock in SOCKET_LIST:
            logging.info("Removing socket %s." % sock)
            SOCKET_LIST.remove(sock)
        else:
            logging.error("Socket %s not in socket list." % sock)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(10)

    # add server socket object to the list of readable connections
    SOCKET_LIST.append(server_socket)

    logging.info("Server started on port " + str(PORT))

    handler = Handler()

    while True:
        handler.work()

        # get the list sockets which are ready to be read through select
        # 4th arg, time_out  = 0 : poll and never block
        ready_to_read, unused_ready_to_write, unused_in_error = select.select(SOCKET_LIST, [], [], 0)

        for sock in ready_to_read:
            # a new connection request recieved
            if sock == server_socket:
                sockfd, addr = server_socket.accept()
                if len(SOCKET_LIST) == 2:
                    logging.warn("Not accepting new connection request from [%s:%s]." % addr)
                else:
                    SOCKET_LIST.append(sockfd)
                    logging.info("Client (%s, %s) connected" % addr)

            # a message from a client, not a new connection
            else:
                # process data recieved from client,
                try:
                    # receiving data from the socket.
                    success, data = recv(sock, RECV_BUFFER)
                    if success:
                        # there is something in the socket
                        if isinstance(data, np.ndarray):
                            handler.enque(data)
                    else:
                        # remove the socket that's broken
                        logging.warn("False data: %s" % typeData(data))

                except Exception:
                    logging.error(traceback.format_exc())
                    continue

    server_socket.close()

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    sys.exit(server())

