from sciibo.core.scene import Scene
from sciibo.graphics import colors
from sciibo.graphics.animations.logo import Logo
from sciibo.graphics.forms import Menu


class Main(Scene):
    def enter(self):
        self.chain = []
        self.set_color(colors.MENU)
        self.erase()

        self.draw_str(20, 27, 'copyright (c) 2017 fdev.nl')
        self.draw_rectangle(10, 31, 8, 18)

        self.add_child(Logo(3, 18))

        items = [
            ('single', 'Single player'),
            ('host', 'Host game'),
            ('join', 'Join game'),
            None,
            ('help', 'Help'),
            ('quit', 'Quit'),
        ]
        self.menu = Menu(11, 33, 14, items, on_select=self.on_menu_select)
        self.add_child(self.menu)

    """
    Form handling
    """
    def on_menu_select(self, key):
        if key == 'single':
            self.state.set_scene("Single")
        elif key == 'host':
            self.state.set_scene("Host")
        elif key == 'join':
            self.state.set_scene("Join")
        elif key == 'help':
            self.state.set_scene("Help")
        elif key == 'quit':
            self.state.quit()

    """
    Input handling
    """
    def on_key(self, ch):
        self.chain = self.chain[-9:] + [ch]
        if self.chain == [259, 259, 258, 258, 260, 261, 260, 261, 98, 97]:
            self.state.set_scene("About")
        else:
            self.menu.on_key(ch)

    def on_mouse(self, chain, y, x):
        self.menu.on_mouse(chain, y, x)
