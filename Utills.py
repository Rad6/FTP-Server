import enum
import os
import logging
import stat
import shutil
import errno


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

    if spcmd[0] == 'MKD':
        CMD_mkd(ftpsocks, basedir, _command)
        return ResState.done

    if spcmd[0] == 'RMD':
        CMD_rmd(ftpsocks, basedir, _command)
        return ResState.done

    
    if spcmd[0] == 'DL':
        CMD_download(ftpsocks, basedir, _command)
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
    elif len(spcmd) == 2:
        if spcmd[1] == '..':
            if basedir == os.getcwd():
                msg += "500 Error."
                pass
            else:
                os.chdir("..")
                msg += "250 Successful Change."
        else:
            try:
                if is_in_directory(spcmd[1], basedir):
                    os.chdir(spcmd[1])
                    msg += "250 Successful Change."
                else:
                    msg = "500 Error."
            except:
                msg = "500 Error."
    else:
        msg += "501 Syntax error in parameter or arguments."
    ftpsocks.socket_cmd.sendall(msg.encode())
    logging.info(f"{ftpsocks.address_cmd} {ftpsocks.address_data} changed dir to {os.getcwd()}")    


def CMD_mkd(ftpsocks, basedir, command):
    spcmd = command.split(" ")
    msg = ""
    if len(spcmd) == 2:
        new_dir = spcmd[1]
        path = os.path.join(basedir, new_dir)
        os.mkdir(path)
        msg += "257 " + str(spcmd[1]) + " created."
        logging.info(f"{ftpsocks.address_cmd} {ftpsocks.address_data} created new directory: {spcmd[1]}")
    elif len(spcmd) == 3 and spcmd[1] == "-i":
        new_file = spcmd[2]
        os.mknod(new_file, 0o600 | stat.S_IRUSR)
        msg += "257 " + str(spcmd[2]) + " created."
        logging.info(f"{ftpsocks.address_cmd} {ftpsocks.address_data} created new file: {spcmd[2]}")
    else:
        msg += "501 Syntax error in parameter or arguments."
        logging.info(f"{ftpsocks.address_cmd} {ftpsocks.address_data} mkd syntax error {spcmd[1]}")

    ftpsocks.socket_cmd.sendall(msg.encode())


def CMD_rmd(ftpsocks, basedir, command):
    spcmd = command.split(" ")
    msg = ""
    if len(spcmd) == 2:
        filename = spcmd[1]
        try:
            os.remove(filename)
            msg += "250 " + str(filename) + " deleted."
            logging.info(f"{ftpsocks.address_cmd} {ftpsocks.address_data} file: {spcmd[1]} deleted")
        except OSError as e:
            msg = "500 Error."
            if e.errno == errno.EISDIR: # is a dir
                logging.info(f"{ftpsocks.address_cmd} {ftpsocks.address_data} RMD: entered a directory instead of file: {spcmd[1]}")
            elif e.errno == errno.ENOENT: # no such file or directory
                logging.info(f"{ftpsocks.address_cmd} {ftpsocks.address_data} RMD: No such a file exists: {spcmd[1]}")
            else:
                raise

    elif len(spcmd) == 3 and spcmd[1] == "-f":
        dirname = spcmd[2]
        try:
            shutil.rmtree(dirname)
            msg += "250 " + str(dirname) + " deleted."
            logging.info(f"{ftpsocks.address_cmd} {ftpsocks.address_data} directory: {spcmd[2]} deleted")
        except OSError as e:
            msg = "500 Error."
            if e.errno == errno.ENOENT: # no such file or directory
                logging.info(f"{ftpsocks.address_cmd} {ftpsocks.address_data} RMD: No such directory exists: {spcmd[2]}")
            else:
                raise
    else:
        msg += "501 Syntax error in parameter or arguments."
        logging.info(f"{ftpsocks.address_cmd} {ftpsocks.address_data} rmd syntax error {spcmd[1]}")

    ftpsocks.socket_cmd.sendall(msg.encode())


def is_in_directory(filepath, directory):
    return os.path.realpath(filepath).startswith(
        os.path.realpath(directory) + os.sep)   

def CMD_download(ftpsocks, basedir, command):
    spcmd = command.split(" ")
    msg = ""
    if len(spcmd) == 1:
        msg  = "501 Syntax error in parameter or arguments."
    elif len(spcmd) == 2:
        if spcmd[1] == "":
            msg  = "501 Syntax error in parameter or arguments."
        else:            
            with open(spcmd[1], 'rb') as file:
                # file
                # for data in file:
                #     print(data)
                #     ftpsocks.socket_data.sendall(data)
                data = file.read(1024)
                while data:
                    ftpsocks.socket_data.sendall(data)
                msg = "226 Successful Download."
    ftpsocks.socket_cmd.sendall(msg.encode())