import socket
import enum

class State(enum.Enum): 
    start        = 1
    authenticate = 4
    quit         = 2 
    waiing       = 3

class Client:
    def __init__(self):
        self.HOST = "localhost"
        self.PORT_COMMAND = 8080
        self.PORT_DATA = 8081
        self.STATE = State.start
        self.authenticated = False

    def run(self):
        socket_command = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_data = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_command.connect((self.HOST, self.PORT_COMMAND))
        socket_data.connect((self.HOST, self.PORT_DATA))

        while True:
            
            _input = input("ftp> ")
            socket_command.sendall(_input.encode())
            if _input == 'QUIT':
                break
            data = socket_command.recv(2048)
            print(data.decode())

            if data.decode() == "226 List transfer done.":
                datadata = socket_data.recv(2048)
                # print(datadata.decode())
                spdata = datadata.decode().split("$$")
                for item in spdata:
                    print(item)
            
            

   
        socket_command.close()
        socket_data.close()

if __name__ == '__main__':
    client = Client()
    client.run()