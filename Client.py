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

            code = data.decode().split(" ")[0]
            if data.decode() == "226 List transfer done.": # LIST response
                datadata = socket_data.recv(2048)
                spdata = datadata.decode().split("$$")
                if spdata[0] == "":
                    pass
                else:
                    for item in spdata:
                        print(item)
            
            if data.decode() == "226 Successful Download.": # DL response
                length_of_data = int(socket_data.recv(1024).decode())
                socket_data.sendall("ok".encode())
                with open(f"dl_{_input.split(' ')[1]}", 'wb') as file_to_write:
                    while True:
                        datadata = socket_data.recv(10)
                        print(datadata)
                        if datadata == "":
                            break
                            file_to_write.write(datadata)
                    file_to_write.close()
            

   
        socket_command.close()
        socket_data.close()

if __name__ == '__main__':
    client = Client()
    client.run()