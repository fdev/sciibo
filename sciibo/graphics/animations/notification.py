from sciibo.core.animation import Animation


class TimedAlert(Animation):
    def __init__(self, alert, timeout=32, on_complete=None):
        super(TimedAlert, self).__init__(alert.y, alert.x, alert.h, alert.w, on_complete=on_complete)
        alert.y = 0
        alert.x = 0
        self.add_child(alert)
        self.timeout = timeout

    def update(self):
        return self.frame < self.timeout
