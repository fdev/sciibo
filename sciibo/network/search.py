import socket
from threading import Timer

from sciibo.core.helpers import valid_string

from .thread import SocketThread


class SearchThread(SocketThread):
    def before_actions(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        self.timeout = Timer(3.0, self.stop)
        self.timeout.start()

        try:
            self.sock.sendto('sciibo/1.0'.encode(), ('255.255.255.255', 5342))

        except:
            self.stop()
            self.trigger('error')

    def action(self):
        name, address = self.sock.recvfrom(4096)
        name = name.decode()  # bytes to string
        if valid_string(name):
            self.trigger('result', name, address)

    def after_actions(self):
        self.timeout.cancel()
        self.trigger('complete')
