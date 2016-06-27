from command import *

class Ftpython(object):

    def __init__(self):
        """
        Creates new command object, calls accept_command
        """
        self.command = Command()
        while True:
            self.accept_command()

    def accept_command(self):
        """
        Prompts user for command
        """
        cmd = raw_input('ftpython> ')
        self.dir_cmd(cmd)

    def dir_cmd(self, cmd):
        """
        Directs a given command to the appropriate action
        """
        parsed_cmd = self.parse_cmd(cmd)
        cmd = parsed_cmd['cmd']
        args = parsed_cmd['args']
        try:
            getattr(self.command, cmd)(args)
        except AttributeError:
            print "Invalid command."
        except TypeError:
            print "Invalid command"

    def parse_cmd(self, cmd):
        """
        Returns a dictionary with a command name and the trailing args
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

def main():
    """
    Creates instances of Ftpython
    """
    Ftpython()

if __name__ == "__main__":
    main()
