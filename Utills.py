import enum
import os
import logging
import stat
import shutil
import errno
import socket
import base64


mail_server = "mail.ut.ac.ir"
mail_port = 25


class FTPSocks:
    def __init__(self, _socket_cmd, _address_cmd, _socket_data, _address_data):
        self.socket_cmd   = _socket_cmd
        self.address_cmd  = _address_cmd
        self.socket_data  = _socket_data
        self.address_data = _address_data


class Mail:
    def __init__(self, _sender_mail, _sender_UN, _sender_PW, _recipient_mail, _subject, _body):
        self.sender_mail = _sender_mail
        self.sender_UN = _sender_UN
        self.sender_PW = _sender_PW
        self.recipient_mail = _recipient_mail
        self.subject = _subject
        self.body = _body


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
            try:
                with open(spcmd[1], 'rb') as file:
                    data_len = str(os.path.getsize(spcmd[1]))
                    sendable_len = ""
                    for _ in range(13 - len(data_len)):
                        sendable_len += '0'
                    sendable_len += data_len
                    ftpsocks.socket_data.sendall(f"{sendable_len}".encode())
                    for data in file:
                            ftpsocks.socket_data.sendall(data)
                    msg = "226 Successful Download."
                    logging.info(f"{ftpsocks.address_cmd} {ftpsocks.address_data} downloaded {spcmd[1]}")
            except:
                msg = "500 Error."

    ftpsocks.socket_cmd.sendall(msg.encode())


def send_email(mail):
    crlf = '\r\n'
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((mail_server, mail_port))
    response = sock.recv(2048)
    print(response.decode()[:-1])
    heloMsg = f"HELO localhost{crlf}"
    sock.sendall(heloMsg.encode())
    respon = sock.recv(2048)
    authMsg = f"AUTH LOGIN{crlf}"
    sock.sendall(authMsg.encode())
    respon = sock.recv(2048)
    un64 = base64.b64encode(mail.sender_UN.encode())
    pw64 = base64.b64encode(mail.sender_PW.encode())
    sock.sendall(un64)
    sock.sendall(crlf.encode())
    respon = sock.recv(2048)
    sock.sendall(pw64)
    sock.sendall(crlf.encode())
    respon = sock.recv(2048)
    print(respon.decode()[:-1])
    fromMsg = f"MAIL FROM: <{mail.sender_mail}>{crlf}"
    sock.sendall(fromMsg.encode())
    respon = sock.recv(2048)
    rcptMsg = f"RCPT TO: <{mail.recipient_mail}> Notify=success,failure,{crlf}"
    sock.sendall(rcptMsg.encode())
    respon = sock.recv(2048)
    dataMsg = f"DATA{crlf}"
    sock.sendall(dataMsg.encode())
    respon = sock.recv(2048)
    subject = f"Subject: {mail.subject}{crlf}{crlf}"
    sock.sendall(subject.encode())
    mailbody = mail.body + crlf
    sock.send(mailbody.encode())
    EndOfData = f"{crlf}.{crlf}"
    sock.send(EndOfData.encode())
    final_respond = sock.recv(2048)
    print(final_respond.decode()[:-1])
    quitMesg = f"QUIT{crlf}"
    sock.send(quitMesg.encode())
    respon = sock.recv(2048)
    sock.close()
    final_respond_sp = final_respond.decode().split(" ")
    if final_respond_sp[2] == "Ok:":
        logging.info(f"Successfully sent email to {mail.recipient_mail}.")
    else:
        logging.info(f"Could not send email to {mail.recipient_mail}.")

