import socket

from .thread import SocketThread


class ListenThread(SocketThread):
    def before_actions(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', 5342))
        self.sock.listen(5)

    def action(self):
        conn, address = self.sock.accept()
        self.trigger('connect', conn, address)
