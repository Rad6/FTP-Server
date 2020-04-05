import socket
import json
import logging
import threading
from Utills import ResState, mapCommands

class ClientThread(threading.Thread):
    def __init__(self, _socket, _address):
        self.socket_client = _socket
        self.address_client = _address
        threading.Thread.__init__(self)

    def run(self):
        msg = ''
        while True:
            data = self.socket_client.recv(2048)
            message = data.decode()

            state = mapCommands(self.socket_client, message)
            if state == ResState.quit:
                break

            self.socket_client.sendall(f"got ur message in state {state.name}".encode())
        
        print ("# Client ", self.address_client , " is gone")
        logging.info(f"{self.address_client} is gone")
        self.socket_client.close()


class Server:
    def __init__(self):
        with open('config.json') as f:
            data = json.load(f)
        self.PORT_COMMAND = data['commandChannelPort']
        self.PORT_DATA = data['dataChannelPort']
        self.HOST = "localhost"
        self.LOGGING = data['logging']['enable']
        self.PATH_LOGGING = data['logging']['path']

        # configuration of logging
        logging.basicConfig(
            filename=self.PATH_LOGGING,
            filemode='a',
            format='%(asctime)s  %(name)s  %(levelname)s  %(message)s',
            level=logging.DEBUG
        )


    def run(self):
        logging.info(
            f"server is now running on data port of {self.PORT_DATA} and command port of {self.PORT_COMMAND}"
        )

        sock_command = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_command.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock_command.bind((self.HOST, 8080))

        while True:
            sock_command.listen(1)
            socket_client, address_client = sock_command.accept()
            print(f"{address_client} is connected")
            logging.info(f"{address_client} is connected")
            thread_client = ClientThread(socket_client, address_client)
            thread_client.start()




if __name__ == '__main__':
    server = Server()
    server.run()