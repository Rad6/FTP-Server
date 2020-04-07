import enum
import os
import logging
import stat
import shutil
import errno
import socket
import base64
import json
from pathlib import Path

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

class User:
    def __init__(self):
        self.username = ""
        self.password = ""
        self.authenticated = False
        self.email    = ""
        self.accounting = False
        self.threshold = 0
        self.capacity = 0
        self.alert = False
        self.authorization = False
        self.admin = False
        self.files = []
    def __str__(self):
        return f"""
            user          : {self.username}\n
            pass          : {self.password}\n
            authorized    : {self.authenticated}\n
            accounting    : {self.accounting}\n
            email         : {self.email}\n
            threshold     : {self.threshold}\n
            capacity      : {self.capacity}\n
            alert         : {self.alert}\n
            authorization : {self.authorization}\n
            admin         : {self.admin}\n
            files         : {self.files}\n
            """
class Dirs:
    def __init__(self, basedir, currdir):
        self.basedir = basedir
        self.currdir = currdir
    def __str__(self):
        return f"""
        basedir: {self.basedir}\n
        currdir: {self.currdir}\n
        """

class ResState(enum.Enum):
    done = 1
    quit = 2
    unknwon = 3

class FTP:
    def __init__(self):
        pass

    def mapCommands(self, user, ftpsocks, _command, dirs):
        self.user = user
        self.ftpsocks = ftpsocks
        self.command = _command
        self.dirs = dirs

        spcmd = _command.split(" ")

        if spcmd[0] == 'QUIT' or len(spcmd[0]) == 0:
            self.CMD_quit()
            return ResState.quit

        if spcmd[0] in ['PWD', 'LIST', 'CWD', 'MKD', 'RMD', 'DL']:
            if not user.authenticated:
                self.ftpsocks.socket_cmd.sendall("530 Not logged in.".encode())
                return ResState.done

        if spcmd[0] == 'PWD' :
            self.CMD_pwd()
            return ResState.done

        if spcmd[0] == 'LIST':
            self.CMD_list()
            return ResState.done

        if spcmd[0] == 'CWD':
            self.CMD_cwd()
            return ResState.done

        if spcmd[0] == 'MKD':
            self.CMD_mkd()
            return ResState.done

        if spcmd[0] == 'RMD':
            self.CMD_rmd()
            return ResState.done

        if spcmd[0] == 'DL':
            self.CMD_download()
            return ResState.done
        
        if spcmd[0] == 'USER':
            self.CMD_user()
            return ResState.done
        
        if spcmd[0] == 'PASS':
            self.CMD_pass()
            return ResState.done

        if spcmd[0] == 'HELP':
            self.CMD_help()
            return ResState.done

        self.CMD_unknwon()
        return ResState.unknwon


    def CMD_quit(self):
        pass
        
    def CMD_pwd(self):
        # cur_dir  = os.getcwd()
        cur_dir = str(self.dirs.currdir)
        formal = cur_dir.split(str(self.dirs.basedir))
        msg = "257 "
        if len(formal[1]) == 0:
            msg += '.'
        else:
            msg += "." + formal[1]
        self.ftpsocks.socket_cmd.sendall(msg.encode())


    def CMD_unknwon(self):
        self.ftpsocks.socket_cmd.sendall("501 Syntax error in parameter or arguments.".encode())


    def CMD_list(self):
        dirs = os.listdir(self.dirs.currdir)
        msg = ""
        for i in range(len(dirs)):
            if i == 0:
                msg += dirs[i]
            else:
                msg += "$$" + dirs[i]
        if msg == "":
            self.ftpsocks.socket_data.sendall("$$".encode())    
        else:
            self.ftpsocks.socket_data.sendall(msg.encode())
        self.ftpsocks.socket_cmd.sendall("226 List transfer done.".encode())

    def CMD_cwd(self):
        spcmd = self.command.split(" ")
        msg = ""
        if len(spcmd) == 1:
            # os.chdir(self.dirs.basedir)
            self.dirs.currdir = self.dirs.basedir
            msg += "250 Successful Change."
        elif len(spcmd) == 2:
            if spcmd[1] == '..':
                if self.dirs.basedir == self.dirs.currdir:
                    msg += "500 Error."
                    pass
                else:
                    # os.chdir("..")
                    self.dirs.currdir = self.dirs.currdir.parent
                    msg += "250 Successful Change."
            else:
                try:
                    # if self.is_in_directory(spcmd[1], self.dirs.basedir):
                    if (self.dirs.currdir / Path(spcmd[1])).is_dir():
                        # os.chdir(spcmd[1])
                        self.dirs.currdir = (self.dirs.currdir / Path(spcmd[1]))
                        msg += "250 Successful Change."
                        logging.info(f"{self.ftpsocks.address_cmd} {self.ftpsocks.address_data} changed dir to {self.dirs.currdir}")
                    else:
                        msg = "500 Error."
                except:
                    msg = "500 Error."
        else:
            msg += "501 Syntax error in parameter or arguments."
        self.ftpsocks.socket_cmd.sendall(msg.encode())


    def CMD_mkd(self):
        spcmd = self.command.split(" ")
        msg = ""
        if len(spcmd) == 2:
            new_dir = spcmd[1]
            path = os.path.join(self.dirs.basedir, new_dir)
            os.mkdir(path)
            msg += "257 " + str(spcmd[1]) + " created."
            logging.info(f"{self.ftpsocks.address_cmd} {self.ftpsocks.address_data} created new directory: {spcmd[1]}")
        elif len(spcmd) == 3 and spcmd[1] == "-i":
            new_file = spcmd[2]
            os.mknod(new_file, 0o600 | stat.S_IRUSR)
            msg += "257 " + str(spcmd[2]) + " created."
            logging.info(f"{self.ftpsocks.address_cmd} {self.ftpsocks.address_data} created new file: {spcmd[2]}")
        else:
            msg += "501 Syntax error in parameter or arguments."
            logging.info(f"{self.ftpsocks.address_cmd} {self.ftpsocks.address_data} mkd syntax error {spcmd[1]}")

        self.ftpsocks.socket_cmd.sendall(msg.encode())


    def CMD_rmd(self):
        spcmd = self.command.split(" ")
        msg = ""
        if len(spcmd) == 2:
            filename = spcmd[1]
            try:
                os.remove(filename)
                msg += "250 " + str(filename) + " deleted."
                logging.info(f"{self.ftpsocks.address_cmd} {self.ftpsocks.address_data} file: {spcmd[1]} deleted")
            except OSError as e:
                msg = "500 Error."
                if e.errno == errno.EISDIR: # is a dir
                    logging.info(f"{self.ftpsocks.address_cmd} {self.ftpsocks.address_data} RMD: entered a directory instead of file: {spcmd[1]}")
                elif e.errno == errno.ENOENT: # no such file or directory
                    logging.info(f"{self.ftpsocks.address_cmd} {self.ftpsocks.address_data} RMD: No such a file exists: {spcmd[1]}")
                else:
                    raise

        elif len(spcmd) == 3 and spcmd[1] == "-f":
            dirname = spcmd[2]
            try:
                shutil.rmtree(dirname)
                msg += "250 " + str(dirname) + " deleted."
                logging.info(f"{self.ftpsocks.address_cmd} {self.ftpsocks.address_data} directory: {spcmd[2]} deleted")
            except OSError as e:
                msg = "500 Error."
                if e.errno == errno.ENOENT: # no such file or directory
                    logging.info(f"{self.ftpsocks.address_cmd} {self.ftpsocks.address_data} RMD: No such directory exists: {spcmd[2]}")
                else:
                    raise
        else:
            msg += "501 Syntax error in parameter or arguments."
            logging.info(f"{self.ftpsocks.address_cmd} {self.ftpsocks.address_data} rmd syntax error {spcmd[1]}")

        self.ftpsocks.socket_cmd.sendall(msg.encode())


    def is_in_directory(self, filepath, directory):
        return os.path.realpath(filepath).startswith(
            os.path.realpath(directory) + os.sep)   

    def CMD_download(self):
        spcmd = self.command.split(" ")
        msg = ""
        if len(spcmd) == 1:
            msg  = "501 Syntax error in parameter or arguments."
        elif len(spcmd) == 2:
            if spcmd[1] == "":
                msg  = "501 Syntax error in parameter or arguments."
            else: 
                try:
                    dl_dir = self.dirs.currdir / Path(spcmd[1])
                    with open(str(dl_dir), 'rb') as file:
                        data_len = str(os.path.getsize(dl_dir))
                        sendable_len = ""
                        for _ in range(13 - len(data_len)):
                            sendable_len += '0'
                        sendable_len += data_len
                        self.ftpsocks.socket_data.sendall(f"{sendable_len}".encode())
                        for data in file:
                                self.ftpsocks.socket_data.sendall(data)
                        msg = "226 Successful Download."
                        logging.info(f"{self.ftpsocks.address_cmd} {self.ftpsocks.address_data} downloaded {spcmd[1]}")
                except Exception as err:
                    print(f"{self.ftpsocks.address_cmd} {self.ftpsocks.address_data}", err)
                    msg = "500 Error."

        self.ftpsocks.socket_cmd.sendall(msg.encode())


    def send_email(self, mail):
        crlf = '\r\n'
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((mail_server, mail_port))
        response = sock.recv(2048)
        print(response.decode()[:-1])
        heloMsg = f"HELO localhost{crlf}"
        sock.sendall(heloMsg.encode())
        response = sock.recv(2048)
        authMsg = f"AUTH LOGIN{crlf}"
        sock.sendall(authMsg.encode())
        response = sock.recv(2048)
        un64 = base64.b64encode(mail.sender_UN.encode())
        pw64 = base64.b64encode(mail.sender_PW.encode())
        sock.sendall(un64)
        sock.sendall(crlf.encode())
        response = sock.recv(2048)
        sock.sendall(pw64)
        sock.sendall(crlf.encode())
        response = sock.recv(2048)
        print(response.decode()[:-1])
        fromMsg = f"MAIL FROM: <{mail.sender_mail}>{crlf}"
        sock.sendall(fromMsg.encode())
        response = sock.recv(2048)
        rcptMsg = f"RCPT TO: <{mail.recipient_mail}> Notify=success,failure,{crlf}"
        sock.sendall(rcptMsg.encode())
        response = sock.recv(2048)
        dataMsg = f"DATA{crlf}"
        sock.sendall(dataMsg.encode())
        response = sock.recv(2048)
        subject = f"Subject: {mail.subject}{crlf}{crlf}"
        sock.sendall(subject.encode())
        mailbody = mail.body + crlf
        sock.send(mailbody.encode())
        EndOfData = f"{crlf}.{crlf}"
        sock.send(EndOfData.encode())
        final_response = sock.recv(2048)
        print(final_response.decode()[:-1])
        quitMesg = f"QUIT{crlf}"
        sock.send(quitMesg.encode())
        response = sock.recv(2048)
        sock.close()
        final_response_sp = final_response.decode().split(" ")
        if final_response_sp[2] == "Ok:":
            logging.info(f"Successfully sent email to {mail.recipient_mail}.")
        else:
            logging.info(f"Could not send email to {mail.recipient_mail}.")

    def CMD_user(self):
        spcmd  = self.command.split(" ")
        msg = ""
        if len(spcmd) != 2:
            msg = "500 Error."
        elif len(spcmd) == 2:
            conf_dir = str(self.dirs.basedir.parent / Path("config.json"))
            # file = open(self.dirs.basedir.split('/ftp')[0] + "/config.json")
            file = open(conf_dir)
            data = json.load(file)
            file.close()
            if spcmd[1] in [item['user'] for item in data['users']]:
                msg = "331 User name okay, need password."
                self.user.username = spcmd[1]
            else:
                msg = "404 Invalid User."

        self.ftpsocks.socket_cmd.sendall(msg.encode())

    def CMD_pass(self):
        spcmd  = self.command.split(" ")
        msg = ""
        if len(spcmd) != 2:
            msg = "500 Error."
        else:
            if not self.user.username:
                msg = '503 Bad sequence of self.commands.'
            else:
                conf_dir = str(self.dirs.basedir.parent / Path("config.json"))
                # file = open(self.dirs.basedir.split('/ftp')[0] + "/config.json")
                file = open(conf_dir)
                data = json.load(file)
                for item in data['users']:
                    if item['user'] == self.user.username:
                        if item['password'] == spcmd[1]:
                            self.user.password = item["password"]
                            self.user.authenticated = True
                            if data['accounting']['enable']:
                                self.user.accounting = True
                                self.user.threshold  = data['accounting']['threshold']
                                for item in data['accounting']['users']:
                                    if item['user'] == self.user.username:
                                        self.user.email = item['email']
                                        self.user.capacity = item['size']
                                        self.user.alert = item['alert']
                                if data['authorization']['enable']:
                                    self.user.authorization = True
                                    if self.user.username in data['authorization']['admins']:
                                        self.user.admin = True
                                        self.user.files = data['authorization']['files']
                            print(self.user)
                            logging.info(f"{self.ftpsocks.address_cmd} {self.ftpsocks.address_data} logedin as {self.user.username}")
                            msg = "230 User logged in, proceed."
                        else:
                            msg = "430 Invalid username or password."
        self.ftpsocks.socket_cmd.sendall(msg.encode())

    def CMD_help(self):
        msg = """214
USER [username] : Its argument is used to specify the user's string. It is used
                  for user authentication.
PASS [password] : Its argument is a password for user's account who has already
                  entered his/her username.
PWD             : Simply shows the current directory that user is in.
MKD -i [name]   : It creates a new file or directory with the given name. With 
                  an -i flag the program makes a new file and otherwise a new 
                  directory.
RMD -f [name]   : Removes a file or directory specified by [name]. The -f flag
                  removes a directory and otherwise a file will be removed!
LIST            : Shows the existing files in the current directory.
CWD [path]      : Changes the current directory to [path]. In case of ".." as 
                  input, program goes to the previous directory and if used 
                  with no argument, current directory changes to root (/ftp).
DL [name]       : It downloads the file specified by [name]
HELP            : Displays this information.
QUIT            : It logs out the user from program."""
        self.ftpsocks.socket_cmd.sendall(msg.encode())
