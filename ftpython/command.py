from connect import *
import sys
import os
import subprocess
import getpass
import inspect

class Command(object):
    """
    Creates new connection object, sets default modes
    """
    def __init__(self):
        self.connection = Connection()
        self.current_dir = os.getcwd()
        self.transfer_type = ('I', 'binary')
        self.logged_in = False
        # Interaction is off by default (user prompts for actions)
        self.interactive = False

    def dir_cmd(self, cmd):
        """
        Directs a given command to the appropriate action
        """
        parsed_cmd = self.parse_cmd(cmd)
        cmd = parsed_cmd['cmd']
        args = parsed_cmd['args']
        try:
            getattr(self, cmd)(args)
        except AttributeError:
            print "Invalid command."

    def parse_cmd(self, cmd):
        """
        Returns a dictionary with a command name and the following args
        """
        cmd = cmd.strip().split(' ')
        name = cmd[0]
        if len(cmd) > 2:
            args = cmd[1:]
        elif len(cmd) == 2:
            args = cmd[1]
        else:
            args = False
        return {
            'cmd': name,
            'args': args
        }

    def open(self, args):
        """
        Accepts a host, connects, then prompts for authentication
        """
        # Don't try to connect if a connection exists
        if not self.connection.connected:
            if not args or type(args) is list:
                self.usage('open some.host.name|XX.XXX.XXX.XXX')
                return False
            connect_code = self.connection.f_connect(args)
            if connect_code == '220':
                # Prompt for username on server's request
                possible_user = getpass.getuser()
                user_name = raw_input('Name(' + self.connection.host + ':' + possible_user + '): ')
                self.connection.send_request('USER '+ user_name)
                response = self.connection.get_response()
                # If the user is good, prompt for password and send
                if response['code'] == '331':
                    self.pass_prompt()
                    # Check if log in is good, then set transfer type to binary
                    if self.logged_in:
                        self.connection.send_request('TYPE I')
                        self.connection.get_response(True)
                        self.type('')
                        # Turn on interactive mode
                        self.interactive = True

            else:
                print "Error: " + args + " is not a valid host."
        else:
            print "You are already connected to: " + self.connection.host + ", type 'close' to disconnect"

    def close(self, args):
        """
        Calls for server connection close
        """
        if self.check_connection():
            # Logsout of the server and closes the connection
            self.connection.send_request('QUIT')
            self.connection.get_response()
            self.connection.f_close()

    def user(self, args):
        """
        Calls the user command for a given username
        """
        if self.check_connection():
            if not args or type(args) is list:
                self.usage('user user_name')
                return False
            self.connection.send_request('USER ' + args)
            response = self.connection.get_response()
            if response['code'] == '331':
                self.pass_prompt()

    def pass_prompt(self):
        """
        Prompts user for password
        """
        password = getpass.getpass('Password: ')
        self.connection.send_request('PASS ' + password)
        response = self.connection.get_response()
        if response['code'] == '230':
            self.logged_in = True
        else:
            print "Login failed."

    def cd(self, args):
        """
        Sends a request to change the current working directory on the server
        """
        if self.check_connection() and self.check_logged_in():
            if not args or type(args) is list:
                self.usage('cd some_directory')
                return False
            self.connection.send_request('CWD ' + args)
            self.connection.get_response()

    def ls(self, args):
        """
        Sends a request to receive the current working directory's contents.
        """
        if self.check_connection() and self.check_logged_in():
            # Create passive connection for file operations
            pasv_con = self.connection.create_pasv_con()
            # Send the list request
            self.connection.send_request('NLST')
            self.connection.get_response()
            # Print out the stream coming in on the file connection
            print pasv_con.recv(4096)
            self.connection.get_response()
            # Close the connection
            pasv_con.close()

    def lcd(self, args):
        """
        Changes the current working directory on the local machine.
        If there are no args, just print it out.
        """
        if args:
            new_dir = args
            try:
                os.chdir(new_dir)
                self.current_dir = os.getcwd()
                print "Local working directory " + self.current_dir
            except OSError:
                print "No such file/directory '" + new_dir + "'"
        else:
            print "Local working directory " + self.current_dir

    def lds(self, args):
        """
        Issues a shell command to get the files in the local working directory
        """
        if not args:
            flag = '-C'
        elif '-l' in args:
            flag = '-l'
        subprocess.call(['ls', flag])

    def cdup(self, args):
        """
        Sends a request to change the current working directory on the server to the parent folder
        """
        if self.check_connection() and self.check_logged_in():
            self.connection.send_request('CDUP')
            self.connection.get_response()

    def pwd(self, args):
        """
        Sends a request for the current working directory on the server
        """
        if self.check_connection() and self.check_logged_in():
            self.connection.send_request('PWD')
            self.connection.get_response()

    def size(self, args):
        """
        Sends a request for the file size of a file on the server
        """
        if self.check_connection() and self.check_logged_in():
            if not args or type(args) is list:
                self.usage('size file.txt')
                return False
            self.connection.send_request('SIZE ' + args)
            # Put response in to a more readable format
            response = self.connection.get_response(True)
            print 'Size:' + response['message'].strip('\r\n') + ' bytes'

    def mkdir(self, args):
        """
        Sends a request to create a directory on the server
        """
        if self.check_connection() and self.check_logged_in():
            if not args or type(args) is list:
                self.usage('mkdir some_directory')
                return False
            self.connection.send_request('MKD ' + args)
            self.connection.get_response()

    def rmdir(self, args):
        """
        Sends a request to delete a directory on the server
        """
        if self.check_connection() and self.check_logged_in():
            if not args or type(args) is list:
                self.usage('rmdir some_directory')
                return False
            if self.m_prompt(args[0]):
                self.connection.send_request('RMD ' + args)
                self.connection.get_response()

    def put(self, args):
        """
        Sends a given file to the server
        """
        if self.check_connection() and self.check_logged_in():
            if not args or type(args) is list:
                self.usage('put file.txt')
                return False
            p_file = args
            if os.path.isfile(p_file):
                # Confirm action
                if self.m_prompt(p_file):
                    # Open file to send
                    to_send = open(p_file, 'rb')
                    # Create passive connection and send request
                    pasv_con = self.connection.create_pasv_con()
                    self.connection.send_request('STOR ' + p_file)
                    self.connection.get_response()
                    # Send the file over the data connection
                    pasv_con.send(to_send.read())
                    # Close passive connection
                    pasv_con.close()
                    # Get the final response
                    self.connection.get_response()
            else:
                print p_file + ": file does not exist"

    def mput(self, args):
        """
        Recursive function to upload several files
        """
        if self.check_connection() and self.check_logged_in():
            if not args:
                self.usage('mput file.txt file_two.txt ...')
                return False
            # Call put action for first file
            self.put(args[0])
            # Remove the last file dealt with
            args.pop(0)
            # If there are files left in args, call function again
            if len(args) > 0:
                self.mput(args)

    def rename(self, args):
        """
        Renames a given file on the server
        """
        if self.check_connection() and self.check_logged_in():
            if not args or len(args) != 2:
                self.usage('rename old_name.txt new_name.txt')
                return False
            # Tell the server what file is being renamed
            self.connection.send_request('RNFR ' + args[0])
            response = self.connection.get_response()
            # Check to see if the file is okay to be renamed
            if response['code'] == '350':
                # Send rename to command with new file name
                self.connection.send_request('RNTO ' + args[1])
                self.connection.get_response()
            else:
                print "File not renamed."

    def cat(self, args):
        """
        Prints out contents of given file
        """
        if self.check_connection() and self.check_logged_in():
            if not args or type(args) is list:
                self.usage('cat file.txt')
                return False
            c_file = args
            # Create passive connection and send request
            pasv_con = self.connection.create_pasv_con()
            self.connection.send_request('RETR ' + c_file)
            # If there is no such file, close data connection and exit function
            response = self.connection.get_response()
            if response['code'] == '550':
                pasv_con.close()
                return False
            while True:
                # Receive data in 1024 byte increments
                recv_data = pasv_con.recv(1024)
                # If there's no more data, break from loop
                if not recv_data:
                    break
                # Print data to terminal
                print recv_data
            # Get confirmation response from server
            self.connection.get_response()
            # Close the file, data connection
            pasv_con.close()

    def get(self, args):
        """
        Gets a given file from the server
        """
        if self.check_connection() and self.check_logged_in():
            if not args or type(args) is list:
                self.usage('get file.txt')
                return False
            g_file = args
            if self.m_prompt(g_file):
                # Create passive connection and send request
                pasv_con = self.connection.create_pasv_con()
                self.connection.send_request('RETR ' + g_file)
                # If there is no such file, close data connection and exit function
                response = self.connection.get_response()
                if response['code'] == '550':
                    pasv_con.close()
                    return False
                # Open a new file on the client side
                to_recv = open(g_file, 'wb')
                while True:
                    # Receive the data on the data connection in 1024 byte increments
                    recv_data = pasv_con.recv(1024)
                    # If there is no more data, break out of the loop
                    if not recv_data:
                        break
                    # Write the data to our file
                    to_recv.write(recv_data)
                # Get confirmation response from server
                self.connection.get_response()
                # Close the file, data connection
                to_recv.close()
                pasv_con.close()

    def mget(self, args):
        """
        Recursive function to get several files
        """
        if self.check_connection() and self.check_logged_in():
            if not args:
                self.usage('mget file.txt file_two.txt ...')
                return False
            # Call delete action for first file
            self.get(args[0])
            # Remove the last file dealt with
            args.pop(0)
            # If there are files left in args, call function again
            if len(args) > 0:
                self.mget(args)

    def delete(self, args):
        """
        Deletes a specified file from the server
        """
        if self.check_connection() and self.check_logged_in():
            if not args or type(args) is list:
                self.usage('delete file.txt')
                return False
            if self.m_prompt(args):
                # Create passive connection
                pasv_con = self.connection.create_pasv_con()
                # Send the request, receive the response
                self.connection.send_request('DELE ' + args)
                self.connection.get_response()
                # Close the passive connection
                pasv_con.close()

    def mdelete(self, args):
        """
        Recursive function to delete several files
        """
        if self.check_connection() and self.check_logged_in():
            if not args:
                self.usage('mdelete file.txt file_two.txt ...')
                return False
            # Call delete action
            self.delete(args[0])
            # Remove the last file dealt with
            args.pop(0)
            # If there are files left in args, call function again
            if len(args) > 0:
                self.mdelete(args)

    def prompt(self, args):
        """
        Toggles interactive mode
        """
        if self.interactive:
            self.interactive = False
            print "Interactive mode off."
        else:
            self.interactive = True
            print "Interactive mode on."

    def type(self, args):
        """
        Returns current transfer mode
        """
        if self.check_connection() and self.check_logged_in():
            print "Using " + self.transfer_type[1] + " mode to transfer files."

    def ascii(self, args):
        """
        Sets transfer type to A (ascii text)
        """
        if self.check_connection() and self.check_logged_in():
            self.connection.send_request('TYPE A')
            response = self.connection.get_response()
            # Set global transfer type
            if not response['error']:
                self.transfer_type = ('A', 'ascii')

    def image(self, args):
        """
        Sets transfer type to I (binary, for image transfer)
        """
        if self.check_connection() and self.check_logged_in():
            self.connection.send_request('TYPE I')
            response = self.connection.get_response()
            # Set global transfer type
            if not response['error']:
                self.transfer_type = ('I', 'binary')

    def check_connection(self):
        """
        Checks if there is a server connection, prints error message if not
        """
        if self.connection.connected:
            return True
        else:
            print "You are not connected to a server."
            return False

    def check_logged_in(self):
        """
        Checks if the user is logged in to the server, prints error messsage
        if not
        """
        if self.logged_in:
            return True
        else:
            print "You are not logged in."
            return False

    def m_prompt(self, args):
        """
        Prompts user to confirm removal actions
        """
        # If interactive mode is off, return True without Prompts
        if not self.interactive:
            return True
        # Get the caller functions name, this will be the action name
        action = inspect.stack()[1][3]
        rm = raw_input(action + ' ' + args + '? [Y/N]: ')
        if rm.lower() == 'y':
            return True
        else:
            print "Action not performed."
            return False

    def usage(self, usage_str):
        """
        Prints the usage for a function if it was not used correctly.
        """
        print "Error: Proper usage is: " + usage_str

    def help(self, args):
        """
        Prints a list of the available commands
        """
        print "Commands:\n"
        print """\tascii\tcat\tcd\tcdup\tclose
        delete\tget\thelp\timage\tlcd
        lds\tls\tmdelete\tmget\tmkdir
        mput\tprompt\tput\tpwd\trename
        rmdirsize\ttype\tuser\n"""

    def quit(self, args):
        """
        Terminates the client
        """
        sys.exit()
