import socket

class Connection(object):

    # Default FTP port is 21
    PORT = 21

    def __init__(self, host, username, password):
        """
        Constructor takes in a host, username, and password
        """
        # Get the actual host if just given a domain
        self.host = socket.gethostbyname(host)
        self.username = username
        self.password = password
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # This will become true when we authenticate to the server
        self.auth = False
        # Connect
        self.f_connect()

    def f_connect(self):
        """
        Connects to server, handles the stream
        """
        self.server.connect((self.host, self.PORT))
        while 1:
            # Call parse_stream and print stream message
            stream = self.parse_stream(self.server.recv(1024))
            print stream['message']
            # If we haven't authed yet, call auth
            if not self.auth:
                self.send_auth(stream['message'])

    def parse_stream(self,stream):
        """
        Returns a dictionary with the 3 digit response code and message
        """
        response_code = stream[:3]
        message = stream[3:]
        return {
           'response': response_code,
           'message': message
        }

    def send_auth(self, stream):
        """
        Sends username and password to ftp server
        """
        self.server.send('USER ' + self.username + '\n')
        self.server.send('PASS ' + self.password + '\n')
        self.auth = True

def main():
    ftp_connection = Connection('some.host.name', 'user_name', 'password')

if __name__ == "__main__":
    main()
