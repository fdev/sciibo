from threading import Thread
import socket
import errno
import time

from sciibo.core.emitter import Emitter


class SocketThread(Thread, Emitter):
    def __init__(self):
        Thread.__init__(self)
        Emitter.__init__(self)
        self.stopped = False

    def stop(self):
        self.stopped = True

    def run(self):
        self.before_actions()

        # Make non-blocking so self.stop has effect
        self.sock.setblocking(0)

        while not self.stopped:
            try:
                self.action()

            except socket.error as error:
                if error.args[0] == errno.EWOULDBLOCK:
                    # No data available, wait a bit
                    time.sleep(0.2)
                    continue

                # Might be connection error
                self.stop()
                self.on_error()

        self.after_actions()
        self.sock.close()

    def action(self):
        raise NotImplementedError

    def before_actions(self):
        pass

    def after_actions(self):
        pass

    def on_error(self):
        pass
