from connect import *
import sys
import getpass

class Command(object):
    """
    Creates new Connection object on creation
    """
    def __init__(self):
        self.connection = Connection()

    def dir_cmd(self, cmd):
        """
        Directs a given command to the appropriate action
        """
        cmd = self.parse_cmd(cmd)
        if cmd['cmd'] == 'open':
            self.open(cmd['args'])
        elif cmd['cmd'] == 'close':
            self.close()
        elif cmd['cmd'] == 'quit':
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
            print "You are already connected to: " + self.connection.host + ", type 'close' to disconnect"

    def close(self):
        """
        Calls for server connection close
        """
        if self.connection.connected:
            # Logsout of the server and closes the connection
            self.connection.send_request('QUIT')
            self.connection.get_response()
            self.connection.f_close()
        else:
            print "You have no open connections."

    def quit(self):
        """
        Terminates the client
        """
        sys.exit()
