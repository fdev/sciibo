import socket

from .thread import SocketThread


class BroadcastThread(SocketThread):
    def before_actions(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', 5342))

    def action(self):
        data, address = self.sock.recvfrom(4096)
        self.trigger('discover', address)

    def send(self, address, data):
        self.sock.sendto(data.encode(), address)
