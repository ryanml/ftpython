from connect import *
import sys
import os
import getpass

class Command(object):
    """
    Creates new Connection object, sets local directory
    """
    def __init__(self):
        self.connection = Connection()
        self.current_dir = os.getcwd()

    def dir_cmd(self, cmd):
        """
        Directs a given command to the appropriate action
        """
        parsed_cmd = self.parse_cmd(cmd)
        cmd = parsed_cmd['cmd']
        args = parsed_cmd['args']
        if cmd == 'open':
            self.open(args)
        elif cmd == 'close':
            self.close()
        elif cmd == 'cd':
            self.change_dir(args)
        elif cmd == 'ls':
            self.list_dir()
        elif cmd == 'lcd':
            self.change_local_dir(args)
        elif cmd == 'cdup':
            self.up_dir()
        elif cmd == 'pwd':
            self.print_dir()
        elif cmd == 'mkdir':
            self.make_dir(args)
        elif cmd == 'rmdir':
            self.remove_dir(args)
        elif cmd == 'delete':
            self.del_file(args)
        elif cmd == 'quit':
            self.quit()
        else:
            return False
        return True

    def parse_cmd(self, cmd):
        """
        Returns a dictionary with a command name and the following args
        """
        cmd = cmd.strip().split(' ')
        name = cmd[0]
        if len(cmd) > 1:
            args = cmd[1]
        else:
            args = False
        return {
            'cmd': name,
            'args': args
        }

    def open(self, args):
        """
        Accepts a host, calls for connect
        """
        # Don't try to connect if a connection exists
        if not self.connection.connected:
            connect_code = self.connection.f_connect(args)
            if connect_code == '220':
                # Prompt for username on server's request
                possible_user = getpass.getuser()
                user_name = raw_input('Name(' + self.connection.host + ':' + possible_user + '): ')
                self.connection.send_request('USER '+ user_name)
                response = self.connection.get_response()
                # If the user is good, prompt for password and send
                if response['code'] == '331':
                    password = getpass.getpass('Password: ')
                    self.connection.send_request('PASS ' + password)
                    response = self.connection.get_response()
            else:
                print "Error: " + args + " is not a valid host."
        else:
            print "You are already connected to: " + self.connection.host + ", type 'close' to disconnect"

    def close(self):
        """
        Calls for server connection close
        """
        if self.check_connection():
            # Logsout of the server and closes the connection
            self.connection.send_request('QUIT')
            self.connection.get_response()
            self.connection.f_close()

    def change_dir(self, args):
        """
        Sends a request to change the current working directory on the server
        """
        if self.check_connection():
            self.connection.send_request('CWD ' + args)
            self.connection.get_response()

    def list_dir(self):
        """
        Sends a request to receive the current working directory's contents.
        """
        if self.check_connection():
            # Create passive connection for file operations
            pasv_con = self.connection.create_pasv_con('NLST')

    def change_local_dir(self, args):
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

    def up_dir(self):
        """
        Sends a request to change the current working directory on the server to the parent folder
        """
        if self.check_connection():
            self.connection.send_request('CDUP')
            self.connection.get_response()

    def print_dir(self):
        """
        Sends a request for the current working directory on the server
        """
        if self.check_connection():
            self.connection.send_request('PWD')
            self.connection.get_response()

    def make_dir(self, args):
        """
        Sends a request to create a directory on the server
        """
        if self.check_connection():
            self.connection.send_request('MKD ' + args)
            self.connection.get_response()

    def remove_dir(self, args):
        """
        Sends a request to delete a directory on the server
        """
        if self.check_connection():
            rm = raw_input('Are you sure you want to remove ' + args + ' ? [Y/N]: ')
            if rm.lower() == 'y':
                self.connection.send_request('RMD ' + args)
                self.connection.get_response()
            else:
                print "Directory not removed."

    def del_file(self, args):
        """
        Deletes a specified file from the server
        """
        if self.check_connection():
            pasv_con = self.connection.create_pasv_con('DELE ' + args)

    def check_connection(self):
        """
        Checks if there is a server connection, prints error message if not
        """
        if self.connection.connected:
            return True
        else:
            print "You are not connected to a server."
            return False

    def quit(self):
        """
        Terminates the client
        """
        sys.exit()
