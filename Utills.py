import enum

class FTPSocks:
    def __init__(self, _socket_cmd, _address_cmd, _socket_data, _address_data):
        self.socket_cmd   = _socket_cmd
        self.address_cmd  = _address_cmd
        self.socket_data  = _socket_data
        self.address_data = _address_data


class ResState(enum.Enum):
    done = 1
    quit = 2
    unknwon = 3

def mapCommands(ftpsocks, _command):
    spcmd = _command.split(" ")
    if spcmd[0] == 'QUIT' or len(spcmd[0]) == 0:
        CMD_quit()
        return ResState.quit
          
    return ResState.unknwon


def CMD_quit():
    pass
    