import socket

class Connection(object):

    # Default FTP port is 21
    PORT = 21

    def __init__(self):
        """
        Constructor sets connected to false
        """
        self.connected = False

    def f_connect(self, host):
        """
        Connects to server given a host
        """
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Return false if an invalid hostname has been given
        try:
            self.host = socket.gethostbyname(host)
        except socket.gaierror:
            return False
        # Connect to given host on port
        self.server.connect((self.host, self.PORT))
        response = self.get_response()
        if not response['error']:
            self.connected = True
        return response['code']

    def f_close(self):
        """
        Closes connection to server
        """
        self.server.close()
        self.connected = False

    def send_request(self, request):
        """
        Sends request to server
        """
        request = request.strip()
        self.server.send(request + '\r\n')

    def send_all(self, data):
        self.server.sendall(data)

    def get_response(self):
        """
        Receives response from server, prints and returns the parsed result
        """
        response = self.server.recv(4096)
        print response
        return self.parse_response(response)

    def parse_response(self, response):
        """
        Returns a dictionary with the 3 digit response code and message
        """
        code = response[:3]
        message = response[3:]
        error = False
        if code[0] == '4' or code[0] == '5':
            error = True
        return {
           'code': code,
           'message': message,
           'error': error
        }

    def create_pasv_con(self, cmd):
        """
        Given a response from an issued PASV command, creates a connection
        to the specified host and port.
        """
        # Issue PASV command
        self.send_request('PASV')
        response = self.get_response()
        # Get the host and port parameters from the response
        params = response['message'].split('(')[1].split(')')[0].split(',')
        file_port = (int(params[4]) * 256) + int(params[5])
        # Set up socket connection and connect it
        file_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        file_conn.connect((self.host, file_port))
        # Send command from command connection
        self.send_request(cmd)
        self.get_response()
        # If the command is calling list, output file connection response. Otherwise, don't (there won't be any response)
        if cmd == 'NLST':
            print file_conn.recv(4096)
            self.get_response()
        # Close the file connection
        file_conn.close()
