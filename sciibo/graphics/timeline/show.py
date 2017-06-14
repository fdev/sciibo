class Show(object):
    def __init__(self, drawable):
        self.drawable = drawable

    def next_frame(self):
        self.drawable.show()
        return False
