from command import *

class Cli(object):

    def __init__(self):
        self.command = Command()
        while True:
            self.accept_command()

    def accept_command(self):
        cmd = raw_input('cmd: ')
        if not self.command.dir_cmd(cmd):
            print 'Invalid command.'

if __name__ == "__main__":
    Cli()
