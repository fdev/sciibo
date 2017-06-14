from sciibo.core.animation import Animation

from .show import Show
from .hide import Hide
from .delay import Delay
from .move import Move
from .resize_card import ResizeCard
from .change_card import ChangeCard


class Timeline(Animation):
    def __init__(self, on_complete=None):
        super(Timeline, self).__init__(0, 0, 0, 0)
        self.on_complete = on_complete
        self.actions = []
        self.action = None

    def update(self):
        while not self.action or not self.action.next_frame():
            if not self.actions:
                if self.on_complete:
                    self.on_complete()
                return False
            self.action = self.actions.pop(0)
        return True

    @staticmethod
    def register_action(name, cls):
        def handle(self, *args, **kwargs):
            self.actions.append(cls(*args, **kwargs))
        setattr(Timeline, name, handle)


# Register timeline actions
Timeline.register_action('show', Show)
Timeline.register_action('hide', Hide)
Timeline.register_action('delay', Delay)
Timeline.register_action('move', Move)
Timeline.register_action('resize_card', ResizeCard)
Timeline.register_action('change_card', ChangeCard)
