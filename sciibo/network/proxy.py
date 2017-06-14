from sciibo.core.emitter import Emitter


class ProxyConnection(Emitter):
    def send(self, data):
        raise NotImplementedError

    def on_receive(self, data):
        type = data.get('type')
        if not type:
            return
        self.trigger('receive', self, data)

    def stop(self):
        pass


def ProxyConnections():
    a = ProxyConnection()
    b = ProxyConnection()
    a.send = b.on_receive
    b.send = a.on_receive
    return a, b
