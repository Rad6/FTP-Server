import enum

class ResState(enum.Enum):
    done = 1
    quit = 2
    unknwon = 3

def mapCommands(_socket, _command):
    spcmd = _command.split(" ")
    if spcmd[0] == 'QUIT' or len(spcmd[0]) == 0:
        CMD_quit()
        return ResState.quit
          
    return ResState.unknwon


def CMD_quit():
    pass
    