import socket

from sciibo.core.helpers import valid_string
from sciibo.network.proxy import ProxyConnections
from sciibo.network.connection import ConnectionThread
from sciibo.server import Server
from sciibo.client import Client
from sciibo.scenes import scenes


class State:
    def __init__(self):
        # Will be set to False when application should quit
        self.running = True

        # Remember the player name across screens
        self.name = ''

        # Current scene
        self.scene = None

        # Set when hosting a game
        self.server = None

        # Set when playing a game
        self.client = None

    def set_scene(self, sceneClass):
        """
        Change the scene, current state will be automatically passed.
        """
        if self.scene:
            self.scene.leave()
        self.scene = getattr(scenes, sceneClass)(self)
        self.scene.enter()

    def set_name(self, name):
        """
        Validate and set the player name.
        """
        name = name.strip()
        if valid_string(name):
            self.name = name[:16]

    def handle_network(self):
        if self.client:
            self.client.handle_network()

    def host_game(self, cards):
        # Create proxy connection
        proxy_server, proxy_client = ProxyConnections()

        # Create server
        try:
            self.server = Server(self.name, cards)
            self.server.start()
        except socket.error:
            # Port already in use
            return False

        # Add local player
        self.client = Client(proxy_client)
        self.server.add_player(self.name, proxy_server, 'local')

        return True

    def join_game(self, address):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(address)

        except socket.error:
            # Could not open connection
            return False

        conn = ConnectionThread(sock)
        conn.start()

        self.client = Client(conn)
        self.client.join(self.name)

        return True

    def local_game(self, bots, cards):
        # Create local server
        self.server = Server(self.name, cards, local=True)
        self.server.start()

        # Add local player
        proxy_server, proxy_client = ProxyConnections()
        self.client = Client(proxy_client)
        self.server.add_player(self.name, proxy_server, 'local')

        # Add bots
        for n in range(bots):
            self.server.add_bot()

    def leave_game(self):
        if self.server:
            self.server.stop()
        self.server = None

        if self.client:
            self.client.stop()
        self.client = None

    def quit(self):
        """
        Mark the state that the application should quit.
        """
        self.running = False

        if self.scene:
            self.scene.leave()

        self.leave_game()
