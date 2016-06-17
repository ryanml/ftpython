from command import *

class Ftpython(object):

    def __init__(self):
        """
        Creates new command object, calls accept_command while true
        """
        self.command = Command()
        while True:
            self.accept_command()

    def accept_command(self):
        """
        Prompts user for command, sends it to director function
        """
        cmd = raw_input('ftpython> ')
        self.command.dir_cmd(cmd)

def main():
    """
    Creates instances of Ftpython
    """
    Ftpython()

if __name__ == "__main__":
    main()
