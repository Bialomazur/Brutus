import asyncore
from attacker.terminal.server.ConnectionHandler import ConnectionHandler
from attacker.util import ts, CONNECTION_CONNECT_TEMPLATE

class Server(asyncore.dispatcher):

    client_number = 0

    def __init__(self, host, port, window, connections):
        asyncore.dispatcher.__init__(self)
        self.create_socket()
        self.set_reuse_addr()
        self.bind((host, port))
        self.window = window
        self._connections = connections
        self.listen(5)

    def handle_accepted(self, sock, addr):
        self.window.Output.addItem(CONNECTION_CONNECT_TEMPLATE.format(time=ts(), addr=addr))
        Server.client_number += 1
        connection = ConnectionHandler(sock, addr, self.window, Server.client_number, self._connections)
        self._connections[Server.client_number] = connection
