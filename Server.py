import socket
import json
import logging
import threading
from Utills import ResState, FTP, FTPSocks, User, Dirs
import os
from pathlib import Path

class ClientThread(threading.Thread):
    def __init__(self, ftpsocks, basedir):
        self.ftpsocks = ftpsocks
        self.dirs = Dirs(basedir, basedir)
        self.user = User()
        threading.Thread.__init__(self)

    def run(self):
        msg = ''
        while True:
            data = self.ftpsocks.socket_cmd.recv(2048)
            message = data.decode()
            ftp = FTP()
            state = ftp.mapCommands(self.user, self.ftpsocks, message, self.dirs)

            if state == ResState.quit:
                self.user = User()
                self.dirs.currdir = self.dirs.basedir
            
            if state == ResState.exit:
                break

        
        print ("# Client ", self.ftpsocks.address_cmd, self.ftpsocks.address_data , " is gone")
        logging.info(f"{self.ftpsocks.address_cmd} {self.ftpsocks.address_data} is gone")

        self.ftpsocks.socket_cmd.close()
        self.ftpsocks.socket_data.close()

class Server:
    def __init__(self):
        with open('config.json') as f:
            data = json.load(f)
        self.PORT_COMMAND = data['commandChannelPort']
        self.PORT_DATA = data['dataChannelPort']
        # self.PORT_COMMAND = 8080
        # self.PORT_DATA = 8081
        self.HOST = "localhost"
        self.LOGGING = data['logging']['enable']
        self.PATH_LOGGING = data['logging']['path']
        self.BASE_DIR = Path.cwd() / Path("ftp")

        # configuration of logging
        logging.basicConfig(
            filename=self.PATH_LOGGING,
            filemode='a',
            format='%(asctime)s  %(name)s  %(levelname)s  %(message)s',
            level=logging.DEBUG
        )

        if not self.LOGGING:
            print("LOGGING IS OFF NOW")
            logging.disable(logging.CRITICAL)

    def run(self):
        logging.info(
            f"server is now running on data port of {self.PORT_DATA} and command port of {self.PORT_COMMAND}"
        )

        sock_command = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_data = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_data.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock_command.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock_command.bind((self.HOST, self.PORT_COMMAND))
        sock_data.bind((self.HOST, self.PORT_DATA))

        while True:
            sock_command.listen()
            sock_data.listen()
            socket_client_cmd, address_client_cmd = sock_command.accept()
            socket_client_data, address_client_data = sock_data.accept()
            ftpsocks = FTPSocks(
                socket_client_cmd, 
                address_client_cmd, 
                socket_client_data, 
                address_client_data
            )
            print(f"{address_client_cmd}{address_client_data} is connected")
            logging.info(f"{address_client_cmd} {address_client_data} is connected")
            thread_client = ClientThread(ftpsocks, self.BASE_DIR)
            thread_client.start()




if __name__ == '__main__':
    server = Server()
    server.run()