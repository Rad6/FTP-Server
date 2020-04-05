# **UT-FTP**
## **first course project,**<br>
    This project is a socket-base cli app (using python) that mimics the FTP Features in its own way.
## **Features:**
1. __Two channels__ for communication (client ports are random)
   * Data channel    (port 20 of the server, given by config file)
   * ‫C‬‬ommand‬‬ ‫‪channel‬‬ (port 21 of the server, given by config file)
2. Running dir is the root of FTP dir
3. __Authentication__ based on config file on server (Auth Sequence)
   * `USER <username>`
   * `331 User name okay, need password.`
     * `PASS <password>`
      * `503 Bad sequence of commands.`
      * `230 User logged in, proceed.`
      * `430 Invalid username or password.`
4. __PWD__: shows where we are as user!
   * `PWD`
     * `257 <working directory path>`
5. __MKD__ (creates new dir) MKD -i (creates new file)
   * `MKD -i <name>`
     * `257 <filename/directory path> created`.
6. __RMD__: Deletes a file or dir, if -f was set, it deletes a dir.
   * `RMD -f <name>` 
     * `250 <filename/directory path> deleted`
7. __LIST__: user can get the list of files in the current dir.
   * `LIST`
   * __note__: the __list__ is sent by __data channel__ then server sent the __msg__ by __command channel__.(client has to see the msg before list of files)
   * `226 List transfer done.`
8. __CWD__: changes the current dir
   * `CWD <path>`
   * `250 Successful Change.`
   * __note__: if path was .. dir should be back to prev dir, if there was no path given, should change the path to the root (first dir)
9. __DL__: downloads the file.
   * `DL <name>`
   * `226 Successfule Download.`
   * __note__: the file is going to be downloaded via the __data channel__ after completion, the __msg__ has to be sent via the __command channel__.
10. __HELP__: shows the commands that server understands with the way they're goning to be used. (sent via __command channel__)
      * `HELP`  
      * `214 USER [name], its ......` 
11. __QUIT__: it just quits :)))
      * `QUIT`
      * `221 Successful Quit.`
12. __global laws__
    1.  in all situations, if user was not authenticated, each commands it requests, the server must response the `332 Need account for login.`
    2.  in all situations, if there was a mistake in flags or params in user commands, the server must response the `501 Syntax error in parameter or arguments.`
    3.  other errors: `500 Error.`
    4.  free format in __data channel__
## **Advance Features:**
13. __Logging__: log file is next to the servers file, if LOG=TRUE in CONFIG file then log all info with data and time(who loged in, name of files that is made or deleted or downloaded). __use append__ to insert to log file.
14. __sending email__: read the detail from the main project description.
15. __accounting__: read the detail from the main project description.

## **Bonus Features:**
16. __Authorization__: read the detail from the main project description.
## _TODO:_
* [ ] Client basis
* [ ] Server basis, make thread for each client


