class Hide(object):
    def __init__(self, drawable):
        self.drawable = drawable

    def next_frame(self):
        self.drawable.hide()
        return False
