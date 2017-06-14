class Emitter(object):
    """
    Simple event emitter.
    """

    def __init__(self):
        self.listeners = dict()

    def on(self, name, cb):
        """
        Register listener for event with name `name`.
        """
        self.listeners.setdefault(name, []).append(cb)

    def off(self, name, cb=None):
        """
        Unregister listener for event with name `name`.
        """
        if cb:
            try:
                self.listeners.setdefault(name, []).remove(cb)
            except ValueError:
                # Don't fail when removing unregistered method
                pass
        else:
            self.listeners[name] = []

    def trigger(self, name, *args, **kwargs):
        """
        Trigger all listeners for specific events.
        Pass along any arguments.
        """
        for cb in self.listeners.get(name, []):
            cb(*args, **kwargs)

    def propagate(self, name):
        """
        Returns a function that retriggers an event.
        """
        def call(*args, **kwargs):
            self.trigger(name, *args, **kwargs)
        return call
