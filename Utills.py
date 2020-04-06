import enum
import os
import logging

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

def mapCommands(ftpsocks, _command, basedir):
    spcmd = _command.split(" ")

    if spcmd[0] == 'QUIT' or len(spcmd[0]) == 0:
        CMD_quit()
        return ResState.quit
    
    if spcmd[0] == 'PWD' :
        CMD_pwd(ftpsocks, basedir)
        return ResState.done

    if spcmd[0] == 'LIST':
        CMD_list(ftpsocks)
        return ResState.done

    if spcmd[0] == 'CWD':
        CMD_cwd(ftpsocks, basedir, _command)
        return ResState.done

    CMD_unknwon(ftpsocks)
    return ResState.unknwon


def CMD_quit():
    pass
    
def CMD_pwd(ftpsocks, basedir):
    cur_dir  = os.getcwd()
    formal = cur_dir.split(basedir)
    msg = "257 "
    if len(formal[1]) == 0:
        msg += '.'
    else:
        msg += "." + formal[1]
    ftpsocks.socket_cmd.sendall(msg.encode())


def CMD_unknwon(ftpsocks):
    ftpsocks.socket_cmd.sendall("501 Syntax error in parameter or arguments.".encode())


def CMD_list(ftpsocks):
    dirs = os.listdir()
    msg = ""
    for i in range(len(dirs)):
        if i == 0:
            msg += dirs[i]
        else:
            msg += "$$" + dirs[i]
    if msg == "":
        ftpsocks.socket_data.sendall("$$".encode())    
    else:
        ftpsocks.socket_data.sendall(msg.encode())
    ftpsocks.socket_cmd.sendall("226 List transfer done.".encode())

def CMD_cwd(ftpsocks, basedir, command):
    spcmd = command.split(" ")
    msg = ""
    if len(spcmd) == 1:
        os.chdir(basedir)
        msg += "250 Successful Change."
    if len(spcmd) == 2:
        if spcmd[1] == '..':
            if basedir == os.getcwd():
                msg += "500 Error."
                pass
            else:
                os.chdir("..")
                msg += "250 Successful Change."
        else:
            try:
                os.chdir(spcmd[1])
                msg += "250 Successful Change."
            except:
                msg = "500 Error."
    else:
        msg += "501 Syntax error in parameter or arguments."
    ftpsocks.socket_cmd.sendall(msg.encode())
    logging.info(f"{ftpsocks.address_cmd} {ftpsocks.address_data} changed dir to {os.getcwd()}")    