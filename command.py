from connect import *
import sys

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
        if not self.connection.connected:
            self.connection.f_connect(args)
        else:
            print "You are already connected to: " + self.connection.host + ", type 'close' to disconnect"

    def close(self):
        """
        Calls for server connection close
        """
        if self.connection.connected:
            self.connection.f_close()
        else:
            print "You have no open connections."

    def quit(self):
        sys.exit()
