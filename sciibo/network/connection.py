import socket
import json
import struct

from sciibo.core.helpers import Queue

from .thread import SocketThread


class ConnectionThread(SocketThread):
    def __init__(self, sock):
        super(ConnectionThread, self).__init__()
        self.sock = sock
        # The number of bytes we are expecting
        self.expecting = None
        # Partial message we received so far
        self.partial = None
        # Outgoing message queue
        self.queue = Queue()
        # Player id this connection belongs to
        self.player = None

    def disconnected(self):
        self.stop()
        self.trigger('receive', self, {'type': 'disconnect'})

    def action(self):
        if not self.expecting:
            # Send messages
            while not self.queue.empty():
                data = self.queue.get()
                message = json.dumps(data)
                self.sock.sendall(struct.pack("i", len(message)) + message.encode())
                self.queue.task_done()

            # Receive message size
            data = self.sock.recv(struct.calcsize("i"))

            if not data:
                self.disconnected()
                return

            # We are now looking for a message
            self.expecting = struct.unpack("i", data)[0]
            self.partial = ""
            return

        # Receive at most what we are expecting
        data = self.sock.recv(self.expecting)

        if not data:
            self.disconnected()
            return

        # Bytes to string
        data = data.decode()

        self.partial += data
        self.expecting -= len(data)

        # Received complete message
        if not self.expecting:
            try:
                data = json.loads(self.partial)
            except ValueError:
                return

            if not isinstance(data, dict):
                return

            type = data.get('type')
            if not type:
                return

            self.trigger('receive', self, data)

            self.expecting = None
            self.partial = None

    def send(self, data):
        self.queue.put(data)

    def on_error(self):
        # Trigger disconnect when an error occurs, but not
        # when the connection was stopped (using after_actions).
        self.disconnected()

    def after_actions(self):
        # Send out queued messages before closing socket
        try:
            while not self.queue.empty():
                data = self.queue.get()
                message = json.dumps(data)
                self.sock.sendall(struct.pack("i", len(message)) + message.encode())
                self.queue.task_done()
        except socket.error:
            return
